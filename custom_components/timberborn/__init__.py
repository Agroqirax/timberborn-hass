"""The Timberborn integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    DATA_COORDINATOR,
    DATA_API,
    DEFAULT_SCAN_INTERVAL,
    CONF_SCAN_INTERVAL,
    PLATFORMS,
)
from .coordinator import TimberbornCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Timberborn from a config entry."""
    from timberborn_http import TimberbornAPI

    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    api = TimberbornAPI(host)

    # Verify connectivity on setup
    try:
        await hass.async_add_executor_job(api.get_levers)
    except Exception as err:
        raise ConfigEntryNotReady(
            f"Cannot connect to Timberborn at {host}: {err}"
        ) from err

    coordinator = TimberbornCoordinator(
        hass=hass,
        api=api,
        instance_name=name,
        scan_interval=scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
        DATA_API: api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
