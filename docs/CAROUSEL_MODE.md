# Carousel Mode

Carousel mode enables automatic rotation through multiple apps with configurable display durations. This feature is perfect for information displays, digital signage, dashboards, and demos.

## Overview

Carousel mode allows you to:
- Automatically cycle through multiple apps
- Set different display durations for each app
- Use each app's saved configuration
- Control rotation via API or web interface
- Persist carousel settings across server restarts

## Features

### Automatic Rotation
- Apps switch automatically after their configured duration
- No manual intervention required
- Seamless transitions between apps

### Flexible Configuration
- Each app can have a different display time
- Duration specified in seconds (1 to 3600)
- Apps can appear multiple times in the rotation

### Persistent State
- Carousel configuration saved to `state.json`
- Settings restored on server restart
- Maintains position in rotation

### Independent App Configs
- Each app uses its own saved configuration
- Configure apps separately from carousel setup
- Update app settings without affecting carousel

## Quick Start

### 1. Configure Your Apps

First, set up the configuration for each app you want in the carousel:

```bash
# Configure clock with red color
curl -X POST http://localhost:5000/api/apps/clock/config \
  -H "Content-Type: application/json" \
  -d '{"color": [255, 0, 0], "font": "tom-thumb"}'

# Configure scroll text with a message
curl -X POST http://localhost:5000/api/apps/scroll_text/config \
  -H "Content-Type: application/json" \
  -d '{"text": "Welcome to RetroBoard!", "color": [0, 255, 0]}'

# Configure stars animation
curl -X POST http://localhost:5000/api/apps/stars/config \
  -H "Content-Type: application/json" \
  -d '{"spawn_rate": 3, "lifetime": 40}'
```

### 2. Enable Carousel

Create a carousel that rotates through your apps:

```bash
curl -X POST http://localhost:5000/api/carousel \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "apps": [
      {"app": "clock", "duration": 10},
      {"app": "scroll_text", "duration": 15},
      {"app": "stars", "duration": 20}
    ]
  }'
```

The display will now show:
- Clock for 10 seconds (in red)
- Scroll text for 15 seconds (in green, "Welcome to RetroBoard!")
- Stars for 20 seconds (spawn rate of 3)
- Then loop back to clock

### 3. Monitor Status

Check carousel status at any time:

```bash
curl http://localhost:5000/api/carousel
```

Response:
```json
{
  "enabled": true,
  "apps": [
    {"app": "clock", "duration": 10},
    {"app": "scroll_text", "duration": 15},
    {"app": "stars", "duration": 20}
  ],
  "current_index": 1
}
```

### 4. Disable Carousel

Stop automatic rotation:

```bash
curl -X POST http://localhost:5000/api/carousel \
  -H "Content-Type: application/json" \
  -d '{"enabled": false, "apps": []}'
```

## API Reference

### GET /api/carousel

Get current carousel configuration.

**Response:**
```json
{
  "enabled": true,
  "apps": [
    {"app": "clock", "duration": 10},
    {"app": "scroll_text", "duration": 15}
  ],
  "current_index": 0
}
```

### POST /api/carousel

Update carousel configuration.

**Request:**
```json
{
  "enabled": true,
  "apps": [
    {"app": "clock", "duration": 10},
    {"app": "scroll_text", "duration": 15},
    {"app": "stars", "duration": 20}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "enabled": true,
  "apps": [...]
}
```

**Parameters:**
- `enabled` (boolean) - Whether carousel is active
- `apps` (array) - List of app configurations
  - `app` (string) - App name (must exist)
  - `duration` (number) - Display time in seconds (must be > 0)

**Validation:**
- At least one app required when enabled
- All app names must be valid
- All durations must be positive numbers

## Python Usage

### Basic Example

```python
import requests

API_BASE = "http://localhost:5000/api"

# Configure apps
requests.post(f"{API_BASE}/apps/clock/config", json={
    "color": [255, 0, 0]
})

requests.post(f"{API_BASE}/apps/scroll_text/config", json={
    "text": "Hello World!",
    "color": [0, 255, 0]
})

# Enable carousel
response = requests.post(f"{API_BASE}/carousel", json={
    "enabled": True,
    "apps": [
        {"app": "clock", "duration": 10},
        {"app": "scroll_text", "duration": 15}
    ]
})

print(response.json())
```

### Helper Functions

```python
def get_carousel_status():
    """Get current carousel configuration."""
    response = requests.get(f"{API_BASE}/carousel")
    return response.json()

def enable_carousel(apps):
    """Enable carousel with list of apps."""
    return requests.post(f"{API_BASE}/carousel", json={
        "enabled": True,
        "apps": apps
    }).json()

def disable_carousel():
    """Disable carousel mode."""
    return requests.post(f"{API_BASE}/carousel", json={
        "enabled": False,
        "apps": []
    }).json()

# Usage
status = get_carousel_status()
print(f"Carousel enabled: {status['enabled']}")

enable_carousel([
    {"app": "clock", "duration": 10},
    {"app": "stars", "duration": 15}
])

disable_carousel()
```

## Web Interface

The web interface provides a visual way to configure carousel mode.

### Accessing Carousel Settings

1. Open the web interface (http://localhost:3000)
2. Scroll down to the "🔄 Carousel Mode" section
3. View current status (Enabled/Disabled)

### Configuring Carousel

1. Click "Configure Carousel" button
2. Check "Enable Carousel Mode" checkbox
3. Click "➕ Add App" to add apps to rotation
4. For each app:
   - Select the app from dropdown
   - Enter duration in seconds
   - Click ❌ to remove if needed
5. Click "Save Carousel" to apply

### Carousel Display

When not editing, the carousel section shows:
- Current status (Enabled/Disabled badge)
- Number of apps in rotation
- List of apps with their durations
- "Configure Carousel" button to edit

## Use Cases

### Information Display

Rotate through different data sources:

```python
carousel_apps = [
    {"app": "clock", "duration": 10},        # Current time
    {"app": "weather", "duration": 15},      # Weather info
    {"app": "news", "duration": 20},         # News headlines
    {"app": "calendar", "duration": 15}      # Today's events
]
```

### Digital Signage

Cycle through promotional content:

```python
carousel_apps = [
    {"app": "scroll_text", "duration": 20},  # Main promotion
    {"app": "clock", "duration": 5},         # Time check
    {"app": "qr_code", "duration": 15},      # QR for details
    {"app": "scroll_text", "duration": 20}   # Secondary message
]
```

### Dashboard

Show multiple metrics:

```python
carousel_apps = [
    {"app": "sales_chart", "duration": 15},
    {"app": "cpu_monitor", "duration": 10},
    {"app": "network_graph", "duration": 15},
    {"app": "clock", "duration": 5}
]
```

### Demo/Showcase

Display all capabilities:

```python
carousel_apps = [
    {"app": "clock", "duration": 8},
    {"app": "scroll_text", "duration": 10},
    {"app": "stars", "duration": 12},
    {"app": "game_of_life", "duration": 15},
    {"app": "weather", "duration": 10}
]
```

## Best Practices

### Duration Guidelines

| App Type | Recommended Duration |
|----------|---------------------|
| Clock | 5-10 seconds |
| Short text | 10-15 seconds |
| Long text | 15-30 seconds |
| Animations | 10-20 seconds |
| Static info | 15-30 seconds |

### Configuration Workflow

1. **Design first** - Plan which apps and durations
2. **Configure apps** - Set up each app's settings
3. **Test individually** - Verify each app works
4. **Enable carousel** - Add apps to rotation
5. **Watch full cycle** - Observe complete rotation
6. **Adjust timing** - Fine-tune durations
7. **Deploy** - Enable for production

### Common Patterns

**Short rotation (under 1 minute):**
```json
[
  {"app": "clock", "duration": 10},
  {"app": "scroll_text", "duration": 15},
  {"app": "stars", "duration": 10}
]
```

**Medium rotation (1-3 minutes):**
```json
[
  {"app": "clock", "duration": 15},
  {"app": "weather", "duration": 30},
  {"app": "news", "duration": 45},
  {"app": "calendar", "duration": 30}
]
```

**Long rotation (3+ minutes):**
```json
[
  {"app": "dashboard", "duration": 60},
  {"app": "metrics", "duration": 45},
  {"app": "clock", "duration": 15},
  {"app": "status", "duration": 60}
]
```

## State Persistence

### Storage Format

Carousel configuration is stored in `state.json`:

```json
{
  "last_app": "clock",
  "app_configs": {...},
  "settings": {...},
  "carousel": {
    "enabled": true,
    "apps": [
      {"app": "clock", "duration": 10},
      {"app": "scroll_text", "duration": 15}
    ],
    "index": 0
  }
}
```

### Automatic Restore

On server restart:
1. Carousel configuration is loaded from `state.json`
2. If enabled, carousel starts automatically
3. Rotation begins with the first app
4. Timer resets (doesn't continue from last position)

### Manual State Management

```bash
# Backup carousel state
cp state.json state_backup.json

# Edit state manually (not recommended)
nano state.json

# Restore from backup
cp state_backup.json state.json

# Restart server to apply
sudo systemctl restart retroboard
```

## Troubleshooting

### Carousel Not Rotating

**Symptoms:**
- Display stuck on one app
- Apps not switching automatically

**Solutions:**
1. Check carousel is enabled:
   ```bash
   curl http://localhost:5000/api/carousel
   ```

2. Verify apps exist:
   ```bash
   curl http://localhost:5000/api/apps
   ```

3. Check server logs:
   ```bash
   tail -f /var/log/retroboard/retroboard.log
   ```

4. Restart carousel:
   ```bash
   curl -X POST http://localhost:5000/api/carousel \
     -d '{"enabled": false, "apps": []}'
   
   curl -X POST http://localhost:5000/api/carousel \
     -d '{"enabled": true, "apps": [...]}'
   ```

### Wrong App Configuration

**Symptoms:**
- Apps show incorrect colors/settings
- Apps use default configuration

**Solution:**
Update app configuration directly:
```bash
curl -X POST http://localhost:5000/api/apps/clock/config \
  -H "Content-Type: application/json" \
  -d '{"color": [255, 0, 0]}'
```

### Duration Issues

**Problem:** Apps switch too quickly/slowly

**Solution:**
Update carousel with new durations:
```bash
curl -X POST http://localhost:5000/api/carousel \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "apps": [
      {"app": "clock", "duration": 15},
      {"app": "scroll_text", "duration": 25}
    ]
  }'
```

### App Crashes in Carousel

**Symptoms:**
- Carousel stops at certain app
- Error messages in logs

**Solution:**
1. Check app logs for errors
2. Test app individually:
   ```bash
   curl -X POST http://localhost:5000/api/switch \
     -d '{"app": "problematic_app"}'
   ```
3. Fix app configuration or remove from carousel

## Advanced Topics

### Dynamic Carousel Updates

Update carousel based on time of day:

```python
import requests
from datetime import datetime

def update_carousel_for_time():
    hour = datetime.now().hour
    
    if 6 <= hour < 12:  # Morning
        apps = [
            {"app": "clock", "duration": 10},
            {"app": "weather", "duration": 15},
            {"app": "news", "duration": 20}
        ]
    elif 12 <= hour < 18:  # Afternoon
        apps = [
            {"app": "clock", "duration": 5},
            {"app": "traffic", "duration": 15},
            {"app": "stocks", "duration": 20}
        ]
    else:  # Evening/Night
        apps = [
            {"app": "clock", "duration": 15},
            {"app": "stars", "duration": 30}
        ]
    
    requests.post("http://localhost:5000/api/carousel", json={
        "enabled": True,
        "apps": apps
    })
```

### Conditional Apps

Include apps based on conditions:

```python
def build_carousel():
    apps = [{"app": "clock", "duration": 10}]
    
    # Add weather if data available
    if weather_data_available():
        apps.append({"app": "weather", "duration": 15})
    
    # Add alerts if any
    if has_alerts():
        apps.append({"app": "alerts", "duration": 20})
    
    # Always end with something nice
    apps.append({"app": "stars", "duration": 15})
    
    return apps
```

### Monitoring Carousel

Track carousel performance:

```python
import time
import requests

def monitor_carousel_rotation():
    """Log each app transition."""
    last_app = None
    start_time = None
    
    while True:
        response = requests.get("http://localhost:5000/api/current")
        current = response.json()["app"]
        
        if current != last_app:
            if last_app and start_time:
                duration = time.time() - start_time
                print(f"{last_app} displayed for {duration:.1f}s")
            
            last_app = current
            start_time = time.time()
            print(f"Now showing: {current}")
        
        time.sleep(1)
```

## Implementation Details

### Architecture

The carousel functionality is implemented in the `ApplicationManager` class:

1. **State Variables:**
   - `carousel_enabled`: Boolean flag
   - `carousel_apps`: List of app/duration pairs
   - `carousel_index`: Current position in rotation
   - `last_carousel_time`: Timestamp of last switch

2. **Main Loop:**
   - Checks elapsed time since last switch
   - Compares to current app's duration
   - Switches to next app when time expires
   - Wraps around to first app after last

3. **Command Processing:**
   - API requests queue carousel commands
   - Commands processed in main loop
   - State changes saved to disk

### Timer Precision

- Timer checks occur every loop iteration (~0.1s)
- Actual duration may be +/- 0.1s from specified
- For most use cases, this precision is sufficient
- For exact timing, consider external scheduling

## Examples

Complete examples are available in `examples/carousel/`:

- `carousel_example.py` - Complete demonstration script
- `README.md` - Detailed examples and use cases
- `QUICKSTART.md` - Quick reference guide

Run the example:
```bash
python3 examples/carousel/carousel_example.py
```

## Related Documentation

- [API.md](API.md) - Complete API reference
- [WEB_INTERFACE.md](WEB_INTERFACE.md) - Web UI documentation
- [STATE_PERSISTENCE.md](STATE_PERSISTENCE.md) - State management
- [APPS.md](APPS.md) - Creating custom apps

## Future Enhancements

Potential improvements for carousel mode:

- **Scheduling** - Different carousels at different times
- **Conditional rotation** - Skip apps based on conditions
- **Priorities** - Some apps shown more frequently
- **Smooth transitions** - Fade effects between apps
- **Preview mode** - Test carousel without enabling
- **Analytics** - Track which apps shown most
- **Remote sync** - Multiple displays with same carousel