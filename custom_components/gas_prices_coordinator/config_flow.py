"""Config flow for Forecast.Solar integration."""
from __future__ import annotations

from typing import Any
import re

import voluptuous as vol

import logging

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelectorConfig,
    SelectSelector,
    SelectOptionDict,
)
from homeassistant.helpers.template import Template

from .const import (
    CONF_MODIFYER,
    CONF_ENTITY_NAME,
    CONF_ADVANCED_OPTIONS,
    CONF_VAT_VALUE,
    CONF_CALCULATION_MODE,
    DEFAULT_MODIFYER,
    CALCULATION_MODE
)

class GasPriceFlowHandler(ConfigFlow):
    """Handle a config flow for GasPrice."""

    def __init__(self, id: str):
        """Initialize ConfigFlow."""
        self.id = id
        self.advanced_options = None
        self.modifyer = None
        self.name = ""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> GasPriceOptionFlowHandler:
        """Get the options flow for this handler."""
        return GasPriceOptionFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        errors = {}
        already_configured = False

        if user_input is not None:
            self.advanced_options = user_input[CONF_ADVANCED_OPTIONS]
            self.name = user_input[CONF_ENTITY_NAME]

            if user_input[CONF_ENTITY_NAME] not in (None, ""):
                self.name = user_input[CONF_ENTITY_NAME]
            NAMED_UNIQUE_ID = self.name + self.id
            try:
                await self.async_set_unique_id(NAMED_UNIQUE_ID)
                self._abort_if_unique_id_configured()
            except Exception as e:
                errors["base"] = "already_configured"
                already_configured = True

            if self.advanced_options:
                return await self.async_step_extra()
            user_input[CONF_VAT_VALUE] = 0
            user_input[CONF_MODIFYER] = DEFAULT_MODIFYER
            user_input[CONF_CALCULATION_MODE] = CALCULATION_MODE["default"]
            if not already_configured:
                return self.async_create_entry(
                    title=self.name,
                    data={},
                    options={
                        CONF_MODIFYER: user_input[CONF_MODIFYER],
                        CONF_ADVANCED_OPTIONS: user_input[CONF_ADVANCED_OPTIONS],
                        CONF_VAT_VALUE: user_input[CONF_VAT_VALUE],
                        CONF_ENTITY_NAME: user_input[CONF_ENTITY_NAME],
                        CONF_CALCULATION_MODE: user_input[CONF_CALCULATION_MODE]
                    },
                )

        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_ENTITY_NAME, default=""): vol.All(vol.Coerce(str)),
                    vol.Optional(CONF_ADVANCED_OPTIONS, default=False): bool,
                },
            ),
        )

    async def async_step_extra(self, user_input=None):
        """Handle VAT, template and calculation mode if requested."""
        await self.async_set_unique_id(self.id)
        self._abort_if_unique_id_configured()
        errors = {}
        already_configured = False

        if user_input is not None:
            user_input[CONF_ENTITY_NAME] = self.name


            if user_input[CONF_ENTITY_NAME] not in (None, ""):
                self.name = user_input[CONF_ENTITY_NAME]
            NAMED_UNIQUE_ID = self.name + self.id
            try:
                await self.async_set_unique_id(NAMED_UNIQUE_ID)
                self._abort_if_unique_id_configured()
            except Exception as e:
                errors["base"] = "already_configured"
                already_configured = True

            template_ok = False
            if user_input[CONF_MODIFYER] in (None, ""):
                user_input[CONF_MODIFYER] = DEFAULT_MODIFYER
            else:
                # Lets try to remove the most common mistakes, this will still fail if the template
                # was writte in notepad or something like that..
                user_input[CONF_MODIFYER] = re.sub(
                    r"\s{2,}", "", user_input[CONF_MODIFYER]
                )

            template_ok = await self._valid_template(user_input[CONF_MODIFYER])

            if not already_configured:
                if template_ok:
                    if "current_price" in user_input[CONF_MODIFYER]:
                        return self.async_create_entry(
                            title=self.name,
                            data={},
                            options={
                                CONF_MODIFYER: user_input[CONF_MODIFYER],
                                CONF_VAT_VALUE: user_input[CONF_VAT_VALUE],
                                CONF_ENTITY_NAME: user_input[CONF_ENTITY_NAME],
                                CONF_CALCULATION_MODE: user_input[CONF_CALCULATION_MODE]
                            },
                        )
                    errors["base"] = "missing_current_price"
                else:
                    errors["base"] = "invalid_template"


        return self.async_show_form(
            step_id="extra",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_VAT_VALUE, default=""
                    ): vol.All(vol.Coerce(float, "must be a number")),
                    vol.Optional(CONF_MODIFYER, default=""): vol.All(vol.Coerce(str)),
                    vol.Optional(CONF_CALCULATION_MODE, default=CALCULATION_MODE["default"]): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=value, label=key)
                                for key, value in CALCULATION_MODE.items() if key != "default"
                            ]
                        ),
                    ),
                },
            ),
        )

    async def _valid_template(self, user_template):
        try:
            #
            ut = Template(user_template, self.hass).async_render(
                current_price=0
            )  # Add current price as 0 as we dont know it yet..

            return True
            if isinstance(ut, float):
                return True
            else:
                return False
        except Exception as e:
            pass
        return False

class GasPriceOptionFlowHandler(OptionsFlow):
    """Handle options."""

    logger = logging.getLogger(__name__)

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.area = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is not None:
            user_input[CONF_ENTITY_NAME] = self.config_entry.options[CONF_ENTITY_NAME]
            template_ok = False
            if user_input[CONF_MODIFYER] in (None, ""):
                user_input[CONF_MODIFYER] = DEFAULT_MODIFYER
            else:
                # Lets try to remove the most common mistakes, this will still fail if the template
                # was written in notepad or something like that..
                user_input[CONF_MODIFYER] = re.sub(
                    r"\s{2,}", "", user_input[CONF_MODIFYER]
                )

            template_ok = await self._valid_template(user_input[CONF_MODIFYER])

            if template_ok:
                if "current_price" in user_input[CONF_MODIFYER]:
                    return self.async_create_entry(title="", data=user_input)
                errors["base"] = "missing_current_price"
            else:
                errors["base"] = "invalid_template"

        calculation_mode_default = self.config_entry.options.get(CONF_CALCULATION_MODE, CALCULATION_MODE["default"])

        return self.async_show_form(
            step_id="init",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_VAT_VALUE,
                        default=self.config_entry.options[CONF_VAT_VALUE],
                    ): vol.All(vol.Coerce(float, "must be a number")),
                    vol.Optional(
                        CONF_MODIFYER, default=self.config_entry.options[CONF_MODIFYER]
                    ): vol.All(vol.Coerce(str)),
                    vol.Optional(CONF_CALCULATION_MODE, default=calculation_mode_default ): SelectSelector(
                        SelectSelectorConfig(
                            options=[
                                SelectOptionDict(value=value, label=key)
                                for key, value in CALCULATION_MODE.items() if key != "default"
                            ]
                        ),
                    ),
                },
            ),
        )

    async def _valid_template(self, user_template):
        try:
            #
            ut = Template(user_template, self.hass).async_render(
                current_price=0
            )  # Add current price as 0 as we dont know it yet..

            return True
            if isinstance(ut, float):
                return True
            else:
                return False
        except Exception as e:
            pass
        return False