"""Energy Zero gas prices component."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .coordinator import EnergyZeroCoordinator
from custom_components.gas_prices_coordinator.init import setup_entry, unload_entry, update_options
from custom_components.gas_prices_coordinator.const import CONF_MODIFYER

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Energy Zero gas prices component from a config entry."""

    modifyer = entry.options[CONF_MODIFYER]
    coordinator = EnergyZeroCoordinator(hass, modifyer = modifyer)

    return await setup_entry(hass, entry, DOMAIN, coordinator)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await unload_entry(hass, entry, DOMAIN)

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    return await update_options(hass, entry)