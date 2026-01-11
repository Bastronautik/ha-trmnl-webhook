"""Data update coordinator for TRMNL."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import Any

import aiohttp

from homeassistant.components.recorder import get_instance, history
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ENTITIES,
    CONF_UPDATE_INTERVAL,
    CONF_WEBHOOK_ID,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    HISTORY_HOURS,
    TRMNL_WEBHOOK_URL,
)

_LOGGER = logging.getLogger(__name__)


class TRMNLCoordinator(DataUpdateCoordinator):
    """Class to manage fetching TRMNL data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.webhook_id = entry.data[CONF_WEBHOOK_ID]
        self.entities = entry.data[CONF_ENTITIES]
        
        update_interval_minutes = entry.data.get(
            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
        )
        update_interval = timedelta(minutes=update_interval_minutes)

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.webhook_id}",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Home Assistant and send to TRMNL."""
        try:
            # Collect entity data
            entity_data = await self._collect_entity_data()
            
            # Create nested structure per entity
            merge_variables = {
                "last_update": dt_util.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            
            # Add each entity as a nested object
            for entity in entity_data:
                entity_id = entity["entity_id"]
                # Create safe key names (replace . with _)
                safe_key = entity_id.replace(".", "_")
                
                # Create entity object
                entity_obj = {
                    "name": entity["name"],
                    "current": str(entity["state"]),
                    "last_changed": entity["last_changed"],
                }
                
                # Add unit if available
                if entity.get("unit"):
                    entity_obj["unit"] = entity["unit"]
                
                # Add 24h statistics if available
                if entity.get("history"):
                    history_data = entity["history"]
                    values = [h["value"] for h in history_data]
                    
                    if values:
                        entity_obj["24h_avg"] = f"{sum(values) / len(values):.2f}"
                        entity_obj["24h_min"] = f"{min(values):.2f}"
                        entity_obj["24h_max"] = f"{max(values):.2f}"
                
                # Add entity object to merge_variables
                merge_variables[safe_key] = entity_obj
            
            # Prepare payload
            payload = {
                "merge_variables": merge_variables
            }
            
            _LOGGER.info("Payload size: ~%d bytes", len(str(payload)))
            _LOGGER.debug("Sending payload to TRMNL: %s", payload)
            
            # Send to TRMNL webhook
            await self._send_to_trmnl(payload)
            
            return {
                "last_update": dt_util.now(),
                "entity_count": len(entity_data),
                "status": "success",
            }
            
        except Exception as err:
            _LOGGER.error("Error updating TRMNL data: %s", err)
            raise UpdateFailed(f"Error communicating with TRMNL: {err}") from err

    async def _collect_entity_data(self) -> list[dict[str, Any]]:
        """Collect data from selected entities."""
        entity_data = []
        
        for entity_id in self.entities:
            state = self.hass.states.get(entity_id)
            if state is None:
                _LOGGER.warning("Entity %s not found", entity_id)
                continue
            
            data = {
                "entity_id": entity_id,
                "name": state.attributes.get("friendly_name", entity_id),
                "state": state.state,
                "unit": state.attributes.get("unit_of_measurement"),
                "last_changed": state.last_changed.strftime("%Y-%m-%d %H:%M:%S"),
            }
            
            # Add historical data if available
            history_data = await self._get_entity_history(entity_id)
            if history_data:
                data["history"] = history_data
            
            entity_data.append(data)
        
        return entity_data

    async def _get_entity_history(self, entity_id: str) -> list[dict[str, Any]] | None:
        """Get historical data for an entity."""
        try:
            end_time = dt_util.now()
            start_time = end_time - timedelta(hours=HISTORY_HOURS)
            
            # Get history from recorder
            history_list = await get_instance(self.hass).async_add_executor_job(
                history.state_changes_during_period,
                self.hass,
                start_time,
                end_time,
                entity_id,
            )
            
            if not history_list or entity_id not in history_list:
                return None
            
            # Process history data - only numeric values
            history_data = []
            for state in history_list[entity_id]:
                try:
                    value = float(state.state)
                    history_data.append({
                        "timestamp": state.last_changed.isoformat(),
                        "value": value,
                    })
                except (ValueError, TypeError):
                    # Skip non-numeric states
                    continue
            
            return history_data if history_data else None
            
        except Exception as err:
            _LOGGER.debug("Could not get history for %s: %s", entity_id, err)
            return None

    async def _send_to_trmnl(self, payload: dict[str, Any]) -> None:
        """Send data to TRMNL webhook."""
        url = TRMNL_WEBHOOK_URL.format(webhook_id=self.webhook_id)
        
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as response:
                        response.raise_for_status()
                        _LOGGER.info(
                            "Successfully sent data to TRMNL webhook %s",
                            self.webhook_id,
                        )
                        return
                        
            except aiohttp.ClientError as err:
                if attempt < max_retries - 1:
                    _LOGGER.warning(
                        "Failed to send to TRMNL (attempt %d/%d): %s. Retrying...",
                        attempt + 1,
                        max_retries,
                        err,
                    )
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                else:
                    _LOGGER.error(
                        "Failed to send to TRMNL after %d attempts: %s",
                        max_retries,
                        err,
                    )
                    raise