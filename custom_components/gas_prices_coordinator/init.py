from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .const import CONF_COORDINATOR, CONF_MODIFYER
from .coordinator import GasPriceCoordinator

PLATFORMS = [Platform.SENSOR]

async def setup_entry(hass: HomeAssistant, entry: ConfigEntry, domain: str, coordinator: GasPriceCoordinator) -> bool:
    """Set up the Energy Zero gas prices component from a config entry."""
    hass.data.setdefault(domain, {})
    hass.data[domain][entry.entry_id] = {
        CONF_COORDINATOR: coordinator,
    }

    # Fetch initial data, so we have data when entities subscribe and set up the platform
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_options))

    return True


async def unload_entry(hass: HomeAssistant, entry: ConfigEntry, domain: str) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[domain].pop(entry.entry_id)

    return unload_ok


async def update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)