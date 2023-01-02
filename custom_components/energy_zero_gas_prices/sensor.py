"""Energy Zero price information service."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HassJob, HomeAssistant
from homeassistant.helpers import event
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import utcnow

from custom_components.gas_prices_coordinator.sensor import GasPriceSensor
from custom_components.gas_prices_coordinator.const import SENSOR_TYPES, CONF_COORDINATOR

from .const import ATTRIBUTION, DOMAIN, ICON

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Energy Zero sensor entries."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][CONF_COORDINATOR]

    # Add an entity for each sensor type
    async_add_entities([
        EnergyZeroSensor(coordinator, description)
        for description in SENSOR_TYPES
    ], True)


class EnergyZeroSensor(GasPriceSensor):
    """Representation of a Energy Zero sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_icon = ICON