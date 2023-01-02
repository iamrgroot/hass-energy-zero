from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable

from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    CURRENCY_EURO,
    VOLUME_CUBIC_METERS,
)
from homeassistant.helpers.typing import StateType

CONF_ENTITY_NAME = "name"
CONF_COORDINATOR = "coordinator"
CONF_MODIFYER = "modifyer"
CONF_ADVANCED_OPTIONS = "advanced_options"
CONF_CALCULATION_MODE = "calculation_mode"
CONF_VAT_VALUE = "VAT_value"

DEFAULT_MODIFYER = "{{current_price}}"

CALCULATION_MODE = { "default": "publish", "rotation": "rotation", "sliding": "sliding", "publish": "publish" }

@dataclass
class GasPriceEntityDescription(SensorEntityDescription):
    """Describes Energy Zero gas price sensor entity."""

    value_fn: Callable[[dict], StateType] = None

SENSOR_TYPES: tuple[GasPriceEntityDescription, ...] = (
    GasPriceEntityDescription(
        key="current_price",
        name="Current gas market price",
        native_unit_of_measurement=f"{CURRENCY_EURO}/{VOLUME_CUBIC_METERS}",
        value_fn=lambda data: data["current_price"],
    ),
)