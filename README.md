# Home Assistant TRMNL Integration

A custom Home Assistant integration to send entity data to your [TRMNL](https://usetrmnl.com/) e-ink display via webhooks, including historical statistics and recent data points.

## ✨ Features

- 🔗 **Multiple webhooks**: Configure multiple independent TRMNL webhooks
- 📊 **Historical statistics**: Automatically calculate 24-hour average, min, max for numeric entities
- 📈 **Recent data points**: Optionally send 0-25 recent data points for trend visualization
- 🎯 **All entity types**: Support for sensors, lights, switches, device trackers, and more
- ⚙️ **Configurable interval**: Update interval from 5 minutes to 24 hours
- 🎨 **UI configuration**: Everything configurable via Home Assistant UI
- 🔄 **Automatic updates**: Periodic updates based on configured interval
- 🛠️ **Manual updates**: Trigger updates via service calls or automations

## 📦 Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right and select "Custom repositories"
4. Add this repository URL: `https://github.com/Bastronautik/ha-trmnl-webhook`
5. Select "Integration" as the category
6. Click "Add"
7. Search for "TRMNL Webhook" and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from the releases page
2. Extract the `custom_components/trmnl_webhook folder` to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## ⚙️ Configuration

### Via UI

1. Go to Settings → Devices & Services
2. Click + Add Integration
3. Search for TRMNL Webhook
4. Enter your TRMNL Webhook ID (found in your TRMNL plugin settings at usetrmnl.com)
5. Give your webhook a friendly name (optional)
6. Select the entities you want to send
7. Set the update interval (default: 60 minutes)
8. Set history data points (0-25, default: 0)
   - Only statistics (avg/min/max/current state)
   - 1-25: Include recent data points for trends
9. Click Submit

### Adding Multiple Webhooks

Repeat the setup steps to configure multiple TRMNL webhooks. Each webhook can have its own entities, update interval, and history settings.

### Modifying Configuration

1. Go to Settings → Devices & Services
2. Find your TRMNL Webhook integration
3. Click Configure
4. Adjust entities, update interval, or history points
6. Click Submit

## 📋 Usage

### Automatic Updates

The integration automatically sends updates to your TRMNL webhook(s) based on the configured interval.

### Manual Updates

Trigger a manual update via service call:

```yaml
service: trmnl_webhook.send_update
data:
  config_entry_id: "abc123def456"
```

### In automations

```yaml
automation:
  - alias: "Update TRMNL on temperature change"
    trigger:
      - platform: state
        entity_id: sensor.temperature_living_room
    action:
      - service: trmnl_webhook.send_update
        data:
          config_entry_id: "abc123def456"
```

## Data Format

The integration sends data in the following nested JSON format:

### Basic

```json
{
  "merge_variables": {
    "last_update": "2026-01-11 17:30:00",
    "sensors": [
      {
        "entity_id": "sensor_living_room_temperature",
        "name": "Living Room Temperature",
        "current": "21.5",
        "last_changed": "2026-01-11 17:25:00",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "unit": "°C",
        "24h_avg": "20.83",
        "24h_min": "18.50",
        "24h_max": "23.20"
      }
    ],
    "lights": [
      {
        "entity_id": "light_living_room",
        "name": "Living Room",
        "current": "on",
        "last_changed": "2026-01-11 15:20:00",
        "icon": "mdi:lightbulb"
      }
    ]
  }
}
```

### With Historic Data Points

```json
{
  "merge_variables": {
    "last_update": "2026-01-11 17:30:00",
    "sensors": [
      {
        "entity_id": "sensor_living_room_temperature",
        "name": "Living Room Temperature",
        "current": "21.5",
        "unit": "°C",
        "last_changed": "2026-01-11 17:25:00",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "24h_avg": "20.83",
        "24h_min": "18.50",
        "24h_max": "23.20",
        "recent_data": [
          {"time": "13:30", "value": "20.10"},
          {"time": "14:00", "value": "20.50"},
          {"time": "14:30", "value": "21.00"},
          {"time": "15:00", "value": "21.30"},
          {"time": "15:30", "value": "21.50"}
        ]
      },
      {
        "entity_id": "sensor_living_room_humidity",
        "name": "Living Room Humidity",
        "current": "65",
        "unit": "%",
        "last_changed": "2026-01-11 17:20:00",
        "icon": "mdi:water-percent",
        "device_class": "humidity",
        "24h_avg": "63.20",
        "24h_min": "58.00",
        "24h_max": "68.50"
      }
    ],
    "lights": [
      {
        "entity_id": "light_living_room",
        "name": "Living Room",
        "current": "on",
        "last_changed": "2026-01-11 15:20:00",
        "icon": "mdi:lightbulb"
      }
    ],
    "switchs": [
      {
        "entity_id": "switch_boiler",
        "name": "Boiler",
        "current": "off",
        "last_changed": "2026-01-11 12:30:00",
        "icon": "mdi:water-boiler"
      }
    ],
    "device_trackers": [
      {
        "entity_id": "device_tracker_phone",
        "name": "Phone",
        "current": "home",
        "last_changed": "2026-01-11 08:15:00",
        "icon": "mdi:cellphone"
      }
    ]
  }
}
```

### Entity Types

Numeric entities (sensors with numeric values):
- `current`: Current state
- `unit`: Unit of measurement
- `last_changed`: Last state change timestamp
- `24h_avg`, `24h_min`, `24h_max`: 24-hour statistics
- `recent_data`: Optional recent data points (if configured)

Non-numeric entities (lights, switches, device trackers, etc.):
- `current:` Current state ("on", "off", "home", etc.)
- `last_changed`: Last state change timestamp

## ℹ️ Troubleshooting

### Webhook Validation Failed

- ✅ Verify your TRMNL Webhook ID is correct
- ✅ Check that your TRMNL account is active
- ✅ Test the webhook manually via the TRMNL website

### No Data Received

- 📋 Check the logs: **Settings → System → Logs**
- 🔍 Verify the selected entities exist and have data
- 🧪 Test with a manual update via service call

### Error: "Payload too large"
- Reduce the number of entities
- Set `history_points` to `0` or a lower value
- TRMNL has a 2KB payload limit

### Integration Not Showing
- Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
- Restart Home Assistant completely
- Check `custom_components/trmnl_webhook/` folder exists

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
