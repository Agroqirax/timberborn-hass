"""Config flow for Timberborn integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    CONF_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


async def validate_host(hass: HomeAssistant, host: str) -> None:
    """Validate that we can connect to the Timberborn server."""
    from timberborn_http import TimberbornAPI

    api = TimberbornAPI(host)
    # Try fetching levers as a connectivity test
    await hass.async_add_executor_job(api.get_levers)


class TimberbornConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Timberborn."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].rstrip("/")
            name = user_input[CONF_NAME]

            # Prevent duplicate entries for same host
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            try:
                await validate_host(self.hass, host)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Error connecting to Timberborn at %s", host)
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_HOST: host,
                        CONF_NAME: name,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_HOST, default="http://localhost:8080"): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> TimberbornOptionsFlow:
        """Return the options flow."""
        return TimberbornOptionsFlow(config_entry)

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> config_entries.ConfigFlowResult:
        """Handle zeroconf discovery."""
        host_ip = (
            discovery_info.ip_address  # preferred in newer HA
            or discovery_info.host
        )
        host = f"http://{host_ip}:{discovery_info.port}"

        await self.async_set_unique_id(host)
        self._abort_if_unique_id_configured()

        # Store for use in the confirmation form
        self._discovered_host = host

        try:
            await validate_host(self.hass, host)
        except Exception:
            return self.async_abort(reason="cannot_connect")

        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Confirm zeroconf discovery."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    CONF_HOST: self._discovered_host,
                    CONF_NAME: user_input[CONF_NAME],
                },
            )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=vol.Schema(
                {vol.Required(CONF_NAME, default=DEFAULT_NAME): str}
            ),
            description_placeholders={"host": self._discovered_host},
        )


class TimberbornOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Timberborn."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=current_interval
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
                }
            ),
        )
