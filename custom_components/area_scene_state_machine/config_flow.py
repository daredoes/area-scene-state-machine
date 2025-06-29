"""Config flow for Area Scenes integration."""

import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import area_registry as ar

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AreaScenesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Area Scenes."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # This integration has only one instance allowed
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Area Scenes", data={})

        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return AreaScenesOptionsFlowHandler(config_entry)


class AreaScenesOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Area Scenes."""

    area_id: str | None

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry
        self.area_id = None

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        area_registry = ar.async_get(self.hass)
        areas = {area.id: area.name for area in area_registry.async_list_areas()}

        if not areas:
            return self.async_abort(reason="no_areas")

        if user_input is not None:
            self.area_id = user_input["area"]
            return await self.async_step_area()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Required("area"): vol.In(areas)}),
        )

    async def async_step_area(self, user_input: dict[str, Any] | None = None):
        """Handle the configuration for a specific area."""
        area_registry = ar.async_get(self.hass)
        area = area_registry.async_get_area(self.area_id) if self.area_id else None
        area_name = area.name if area else "unknown_area"

        # Get existing customizations for this area
        customize_data = self.config_entry.options.get("customize", {})
        area_config = customize_data.get(self.area_id, {})

        if user_input is not None:
            # Update the customization for the selected area
            new_customize_data = customize_data.copy()
            new_customize_data[self.area_id] = {
                "name": user_input.get("name"),
                "icon": user_input.get("icon"),
                "color": user_input.get("color"),
                "reset_mode": user_input.get("reset_mode", False),
            }
            # Create a new entry with the updated options
            return self.async_create_entry(
                title="", data={"customize": new_customize_data}
            )

        options_schema = vol.Schema(
            {
                vol.Optional(
                    "name", description={"suggested_value": area_config.get("name")}
                ): str,
                vol.Optional(
                    "icon", description={"suggested_value": area_config.get("icon")}
                ): str,
                vol.Optional(
                    "color", description={"suggested_value": area_config.get("color")}
                ): str,
                vol.Optional(
                    "reset_mode", default=area_config.get("reset_mode", False)
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="area",
            data_schema=options_schema,
            description_placeholders={"area_name": area_name},
        )
