from __future__ import annotations

import asyncio
from datetime import timedelta, timezone
from typing import Literal
import pandas as pd
import logging


from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.template import Template, attach
from jinja2 import pass_context
import requests

from .const import DEFAULT_TEMPLATE, UPDATE_INTERVAL, BASE_API_URL



class EasyEnergyCoordinator(DataUpdateCoordinator):
    """Get the latest data and update the states."""

    def __init__(self, hass: HomeAssistant, modifyer: Literal) -> None:
        """Initialize the data object."""
        self.hass = hass
        self.modifyer = modifyer

        # Check incase the sensor was setup using config flow.
        # This blow up if the template isnt valid.
        if not isinstance(self.modifyer, Template):
            if self.modifyer in (None, ""):
                self.modifyer = DEFAULT_TEMPLATE
            self.modifyer = cv.template(self.modifyer)
        # check for yaml setup.
        else:
            if self.modifyer.template in ("", None):
                self.modifyer = cv.template(DEFAULT_TEMPLATE)

        attach(self.hass, self.modifyer)

        logger = logging.getLogger(__name__)
        super().__init__(
            hass,
            logger,
            name="Easy Energy coordinator",
            update_interval=UPDATE_INTERVAL,
        )

    def calc_price(self, value, fake_dt=None, no_template=False) -> float:
        """Calculate price based on the users settings."""

        # Used to inject the current hour.
        # so template can be simplified using now
        if no_template:
            price = round(value, 5)
            return price

        else:
            price = value
            if fake_dt is not None:

                def faker():
                    def inner(*args, **kwargs):
                        return fake_dt

                    return pass_context(inner)

                template_value = self.modifyer.async_render(now=faker(), current_price=price)
            else:
                template_value = self.modifyer.async_render()

            price = round(template_value, 5)

            return price

    def parse_hourprices(self, hourprices):
        for hour, price in hourprices.items():
            hourprices[hour] = self.calc_price(value=price, fake_dt=hour)
        return hourprices

    async def _async_update_data(self) -> dict:
        """Get the latest data from Easy Energy"""
        self.logger.debug("Fetching Easy Energy data")

        time_zone = dt.now().tzinfo
        # We request data for today up until tomorrow.
        today = pd.Timestamp.now(tz=str(time_zone)).replace(hour=0, minute=0, second=0)

        tomorrow = today + pd.Timedelta(hours=47)

        data = await self.fetch_prices(today, tomorrow)

        parsed_data = self.parse_hourprices(data)
        data_all = parsed_data.to_dict()
        data_today = parsed_data[:24].to_dict()
        data_tomorrow = parsed_data[24:48].to_dict()

        return {
            "data": data_all,
            "dataToday": data_today,
            "dataTomorrow": data_tomorrow,
        }

    async def fetch_prices(self, start_date: pd.Timestamp, end_date: pd.Timestamp):
        try:
            # run api_update in async job
            resp = await self.hass.async_add_executor_job(
                self.api_update, start_date, end_date
            )

            return resp

        except (asyncio.TimeoutError, KeyError) as error:
            raise UpdateFailed(f"Fetching energy price data failed: {error}") from error

    def api_update(self, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.Series:
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1"
        }

        params = {
            'startTimestamp': start_date.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
            'endTimestamp': end_date.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
            'includeVat': 'true',
        }

        response = requests.get(BASE_API_URL, params=params, headers=headers)

        data = response.json()

        series = pd.Series(dtype='float64')
        for price in data:
            series[dt.parse_datetime(price["Timestamp"])] = price['TariffUsage']

        return series

    def processed_data(self):
        return {
            "current_price": self.get_current_hourprice(self.data["data"]),
            "next_hour_price": self.get_next_hourprice(self.data["data"]),
            "min_price": self.get_min_price(self.data["dataToday"]),
            "max_price": self.get_max_price(self.data["dataToday"]),
            "avg_price": self.get_avg_price(self.data["dataToday"]),
            "time_min": self.get_min_time(self.data["dataToday"]),
            "time_max": self.get_max_time(self.data["dataToday"]),
            "prices_today": self.get_timestamped_prices(self.data["dataToday"]),
            "prices_tomorrow": self.get_timestamped_prices(self.data["dataTomorrow"]),
            "prices": self.get_timestamped_prices(self.data["data"]),
        }

    def get_next_hourprice(self, hourprices) -> int:
        for hour, price in hourprices.items():
            if hour - timedelta(hours=1) <= dt.utcnow() < hour:
                return price

    def get_current_hourprice(self, hourprices) -> int:
        for hour, price in hourprices.items():
            if hour <= dt.utcnow() < hour + timedelta(hours=1):
                return price

    def get_hourprices(self, hourprices) -> list:
        return [a for a in hourprices.values()]

    def get_avg_price(self, hourprices):
        return round(sum(hourprices.values()) / len(hourprices.values()), 5)

    def get_max_price(self, hourprices):
        return max(hourprices.values())

    def get_min_price(self, hourprices):
        return min(hourprices.values())

    def get_max_time(self, hourprices):
        return max(hourprices, key=hourprices.get)

    def get_min_time(self, hourprices):
        return min(hourprices, key=hourprices.get)

    def get_timestamped_prices(self, hourprices):
        list = []
        for hour, price in hourprices.items():
            str_hour = str(hour)
            list.append({"time": str_hour, "price": price})
        return list