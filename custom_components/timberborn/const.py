"""Constants for the Timberborn integration."""

DOMAIN = "timberborn"

CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 30  # seconds
DEFAULT_NAME = "Timberborn"

PLATFORMS = ["binary_sensor", "light"]

# Data keys stored in hass.data[DOMAIN][entry_id]
DATA_COORDINATOR = "coordinator"
DATA_API = "api"
