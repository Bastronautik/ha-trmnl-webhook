"""The TRMNL integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    SERVICE_SEND_UPDATE,
)
from .coordinator import TRMNLCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TRMNL from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = TRMNLCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Setup platforms (button for manual refresh)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register service for manual updates
    async def handle_send_update(call: ServiceCall) -> None:
        """Handle the send_update service call."""
        config_entry_id = call.data.get("config_entry_id")
        
        if config_entry_id and config_entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][config_entry_id]
            await coordinator.async_request_refresh()
        else:
            _LOGGER.error("Invalid config_entry_id: %s", config_entry_id)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_UPDATE,
        handle_send_update,
        schema=vol.Schema({
            vol.Required("config_entry_id"): cv.string,
        }),
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
