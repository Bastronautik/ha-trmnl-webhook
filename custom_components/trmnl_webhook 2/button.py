"""Button platform for TRMNL Webhook."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import TRMNLCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TRMNL button entity."""
    coordinator: TRMNLCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([TRMNLRefreshButton(coordinator, entry)])


class TRMNLRefreshButton(CoordinatorEntity[TRMNLCoordinator], ButtonEntity):
    """Button to manually refresh TRMNL webhook."""

    def __init__(self, coordinator: TRMNLCoordinator, entry: ConfigEntry) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_name = f"{entry.title} Refresh"
        self._attr_unique_id = f"{entry.entry_id}_refresh"
        self._attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()
