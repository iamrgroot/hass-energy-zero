from __future__ import annotations

from datetime import timezone
from typing import Literal
import pandas as pd
from homeassistant.core import HomeAssistant
from homeassistant.util import dt
import requests
from custom_components.gas_prices_coordinator.coordinator import GasPriceCoordinator

from .const import UPDATE_INTERVAL, BASE_API_URL

class EnergyZeroCoordinator(GasPriceCoordinator):
    """Get the latest data and update the states."""

    def __init__(self, hass: HomeAssistant, modifyer: Literal) -> None:
        """Initialize the data object."""
        super().__init__(
            hass,
            update_interval=UPDATE_INTERVAL,
            modifyer=modifyer
        )

    def api_update(self, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.Series:
        headers = {
            'authority': 'api.energyzero.nl',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'dnt': '1',
            'origin': 'https://www.mijndomein.nl',
            'pragma': 'no-cache',
            'referer': 'https://www.mijndomein.nl/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        }

        params = {
            'fromDate': start_date.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
            'tillDate': end_date.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),
            'interval': '4',
            'usageType': '3',
            'inclBtw': 'true',
        }

        response = requests.get(BASE_API_URL, params=params, headers=headers)

        data = response.json()

        series = pd.Series(dtype='float64')
        for price in data["Prices"]:
            series[dt.parse_datetime(price["readingDate"])] = price['price']

        return series
