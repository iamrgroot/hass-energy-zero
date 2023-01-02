"""Config flow for Energy Zero integration."""

from homeassistant.helpers.template import Template
from custom_components.gas_prices_coordinator.config_flow import GasPriceFlowHandler

from .const import (
    DOMAIN,
    UNIQUE_ID,
)

class EnergyZeroFlowHandler(GasPriceFlowHandler, domain=DOMAIN):
    """Handle a config flow for Energy Zero."""

    def __init__(self):
        """Initialize ConfigFlow."""
        super().__init__(id=UNIQUE_ID)
