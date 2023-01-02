
from dataclasses import dataclass
from collections.abc import Callable
from datetime import timedelta

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import (
    CURRENCY_EURO,
    VOLUME_CUBIC_METERS,
)

from homeassistant.helpers.typing import StateType

DOMAIN = "easy_energy_gas_prices"

ATTRIBUTION = "Data provided by Easy Energy API"
ICON = "mdi:currency-eur"
UNIQUE_ID = f"{DOMAIN}_component"
COMPONENT_TITLE = "Gas prices"

CONF_COORDINATOR = "coordinator"
CONF_MODIFYER = "modifyer"

BASE_API_URL = 'https://mijn.easyenergy.com/nl/api/tariff/getlebatariffs'
UPDATE_INTERVAL = timedelta(hours=1)

DEFAULT_TEMPLATE = "{{current_price}}"

@dataclass
class EasyEnergyEntityDescription(SensorEntityDescription):
    """Describes EasyEnergy gas price sensor entity."""

    value_fn: Callable[[dict], StateType] = None

SENSOR_TYPES: tuple[EasyEnergyEntityDescription, ...] = (
    EasyEnergyEntityDescription(
        key="current_price",
        name="Current gas market price",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{VOLUME_CUBIC_METERS}",
        value_fn=lambda data: data["current_price"],
    ),
    # TODO add other sensors
)