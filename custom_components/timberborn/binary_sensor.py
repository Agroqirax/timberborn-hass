"""Binary sensor platform for Timberborn — represents Adapters (read-only)."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import TimberbornCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Timberborn adapter binary sensors from a config entry."""
    coordinator: TimberbornCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    entities = [
        TimberbornAdapterSensor(coordinator, entry, adapter_name)
        for adapter_name in coordinator.data["adapters"]
    ]

    async_add_entities(entities)


class TimberbornAdapterSensor(CoordinatorEntity[TimberbornCoordinator], BinarySensorEntity):
    """Represents a Timberborn Adapter as a binary sensor (read-only)."""

    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: TimberbornCoordinator,
        entry: ConfigEntry,
        adapter_name: str,
    ) -> None:
        """Initialise the adapter sensor."""
        super().__init__(coordinator)
        self._adapter_name = adapter_name
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_adapter_{adapter_name}"
        self._attr_name = adapter_name

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
    def is_on(self) -> bool | None:
        """Return True if the adapter is active/on."""
        adapters = self.coordinator.data.get("adapters", {})
        adapter = adapters.get(self._adapter_name)
        if adapter is None:
            return None
        return adapter["state"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        return {
            "adapter_name": self._adapter_name,
            "instance": self._entry.data.get("name"),
        }
