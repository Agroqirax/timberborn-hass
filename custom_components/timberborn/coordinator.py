"""DataUpdateCoordinator for Timberborn."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class TimberbornCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to poll the Timberborn API for all entity states."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: Any,
        instance_name: str,
        scan_interval: int,
    ) -> None:
        """Initialise coordinator."""
        self.api = api
        self.instance_name = instance_name

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{instance_name}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all lever and adapter states from the API."""
        try:
            levers = await self.hass.async_add_executor_job(self.api.get_levers)
            adapters = await self.hass.async_add_executor_job(self.api.get_adapters)

            lever_data: dict[str, dict] = {}
            for lever in levers:
                lever_data[lever.name] = {
                    "name": lever.name,
                    "state": await self.hass.async_add_executor_job(
                        self.api.get_lever_state, lever.name
                    ),
                    "spring_return": await self.hass.async_add_executor_job(
                        self.api.get_lever_spring_return, lever.name
                    ),
                }

            adapter_data: dict[str, dict] = {}
            for adapter in adapters:
                adapter_data[adapter.name] = {
                    "name": adapter.name,
                    "state": await self.hass.async_add_executor_job(
                        self.api.get_adapter_state, adapter.name
                    ),
                }

            return {
                "levers": lever_data,
                "adapters": adapter_data,
            }

        except Exception as err:
            raise UpdateFailed(f"Error communicating with Timberborn API: {err}") from err
