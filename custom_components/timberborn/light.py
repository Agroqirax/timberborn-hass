"""Light platform for Timberborn — represents Levers with on/off and RGB color."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR, DATA_API
from .coordinator import TimberbornCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Timberborn lever lights from a config entry."""
    coordinator: TimberbornCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    api = hass.data[DOMAIN][entry.entry_id][DATA_API]

    entities = [
        TimberbornLeverLight(coordinator, entry, api, lever_name)
        for lever_name in coordinator.data["levers"]
    ]

    async_add_entities(entities)


class TimberbornLeverLight(CoordinatorEntity[TimberbornCoordinator], LightEntity):
    """Represents a Timberborn Lever as an RGB light entity."""

    _attr_has_entity_name = True
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}

    def __init__(
        self,
        coordinator: TimberbornCoordinator,
        entry: ConfigEntry,
        api: Any,
        lever_name: str,
    ) -> None:
        """Initialise the lever light."""
        super().__init__(coordinator)
        self._lever_name = lever_name
        self._entry = entry
        self._api = api
        self._attr_unique_id = f"{entry.entry_id}_lever_{lever_name}"
        self._attr_name = lever_name
        # Track color locally since the API has no get_color endpoint
        self._rgb_color: tuple[int, int, int] = (255, 255, 255)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info grouping all entities for this instance."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.data.get("name", "Timberborn"),
            manufacturer="Timberborn",
            model="HTTP Mod",
        )

    @property
    def _lever_data(self) -> dict | None:
        return self.coordinator.data.get("levers", {}).get(self._lever_name)

    @property
    def is_on(self) -> bool | None:
        """Return True if the lever is on."""
        if self._lever_data is None:
            return None
        return self._lever_data["state"]

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return the current RGB color."""
        return self._rgb_color

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        attrs: dict[str, Any] = {
            "lever_name": self._lever_name,
            "instance": self._entry.data.get("name"),
        }
        if self._lever_data:
            attrs["spring_return"] = self._lever_data.get("spring_return")
        return attrs

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the lever on, optionally setting a new RGB color."""
        if ATTR_RGB_COLOR in kwargs:
            r, g, b = kwargs[ATTR_RGB_COLOR]
            hex_color = f"{r:02x}{g:02x}{b:02x}"
            _LOGGER.debug("Setting color of lever '%s' to #%s",
                          self._lever_name, hex_color)
            await self.hass.async_add_executor_job(
                self._api.set_color, self._lever_name, hex_color
            )
            self._rgb_color = (r, g, b)

        await self.hass.async_add_executor_job(
            self._api.switch_on, self._lever_name
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the lever off."""
        await self.hass.async_add_executor_job(
            self._api.switch_off, self._lever_name
        )
        await self.coordinator.async_request_refresh()
