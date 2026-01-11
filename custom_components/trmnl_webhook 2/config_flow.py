"""Config flow for TRMNL integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_ENTITIES,
    CONF_NAME,
    CONF_UPDATE_INTERVAL,
    CONF_WEBHOOK_ID,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
    TRMNL_WEBHOOK_URL,
)

_LOGGER = logging.getLogger(__name__)


class TRMNLConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TRMNL."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate webhook ID
            webhook_id = user_input[CONF_WEBHOOK_ID]
            
            if await self._validate_webhook(webhook_id):
                # Create unique ID based on webhook ID
                await self.async_set_unique_id(webhook_id)
                self._abort_if_unique_id_configured()
                
                # Use custom name or fallback to webhook ID
                title = user_input.get(CONF_NAME) or f"TRMNL Webhook {webhook_id[:8]}..."
                
                return self.async_create_entry(
                    title=title,
                    data=user_input,
                )
            else:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required(CONF_WEBHOOK_ID): str,
            vol.Optional(CONF_NAME): str,
            vol.Required(CONF_ENTITIES): EntitySelector(
                EntitySelectorConfig(
                    domain="sensor",
                    multiple=True,
                )
            ),
            vol.Optional(
                CONF_UPDATE_INTERVAL,
                default=DEFAULT_UPDATE_INTERVAL,
            ): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_UPDATE_INTERVAL,
                    max=MAX_UPDATE_INTERVAL,
                    mode=NumberSelectorMode.BOX,
                    unit_of_measurement="minutes",
                )
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def _validate_webhook(self, webhook_id: str) -> bool:
        """Validate the webhook ID by testing the connection."""
        url = TRMNL_WEBHOOK_URL.format(webhook_id=webhook_id)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Send a test payload with merge_variables wrapper
                test_payload = {
                    "merge_variables": {
                        "test": "true",
                        "message": "Home Assistant TRMNL integration test",
                    }
                }
                async with session.post(
                    url,
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    # Accept both 200 and 201 as valid responses
                    return response.status in [200, 201]
        except Exception as err:
            _LOGGER.error("Error validating webhook: %s", err)
            return False

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return TRMNLOptionsFlow()


class TRMNLOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for TRMNL."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Prepare updated data
            updated_data = dict(self.config_entry.data)
            updated_data[CONF_ENTITIES] = user_input[CONF_ENTITIES]
            updated_data[CONF_UPDATE_INTERVAL] = user_input[CONF_UPDATE_INTERVAL]
            
            # Update name if provided
            if user_input.get(CONF_NAME):
                updated_data[CONF_NAME] = user_input[CONF_NAME]
                new_title = user_input[CONF_NAME]
            else:
                new_title = self.config_entry.title
            
            # Update the config entry
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=updated_data,
                title=new_title,
            )
            
            # Reload to apply changes
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            
            return self.async_create_entry(title="", data={})

        # Get current values
        current_entities = self.config_entry.data.get(CONF_ENTITIES, [])
        if not isinstance(current_entities, list):
            current_entities = [current_entities] if current_entities else []

        current_interval = self.config_entry.data.get(
            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
        )
        
        current_name = self.config_entry.data.get(CONF_NAME, "")

        # Build the form schema
        data_schema = vol.Schema({
            vol.Optional(CONF_NAME, default=current_name): str,
            vol.Required(CONF_ENTITIES, default=current_entities): EntitySelector(
                EntitySelectorConfig(
                    domain="sensor",
                    multiple=True,
                )
            ),
            vol.Optional(CONF_UPDATE_INTERVAL, default=current_interval): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_UPDATE_INTERVAL,
                    max=MAX_UPDATE_INTERVAL,
                    mode=NumberSelectorMode.BOX,
                    unit_of_measurement="minutes",
                )
            ),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )