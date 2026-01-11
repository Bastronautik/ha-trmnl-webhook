"""Constants for the TRMNL integration."""

DOMAIN = "trmnl_webhook"

# Configuration keys
CONF_WEBHOOK_ID = "webhook_id"
CONF_ENTITIES = "entities"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_NAME = "name"

# Defaults
DEFAULT_UPDATE_INTERVAL = 60  # minutes
MIN_UPDATE_INTERVAL = 5  # minutes
MAX_UPDATE_INTERVAL = 1440  # 24 hours in minutes

# TRMNL API
TRMNL_WEBHOOK_URL = "https://usetrmnl.com/api/custom_plugins/{webhook_id}"

# History
HISTORY_HOURS = 24

# Service names
SERVICE_SEND_UPDATE = "send_update"