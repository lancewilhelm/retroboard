# Carousel Mode Examples

This directory contains examples demonstrating how to use RetroBoard's carousel mode to automatically rotate through multiple apps.

## What is Carousel Mode?

Carousel mode allows you to automatically cycle through multiple apps with configurable display durations. This is perfect for:

- **Information displays** - Rotate through different data sources (weather, news, time, etc.)
- **Digital signage** - Cycle through promotional messages and announcements
- **Dashboards** - Show different metrics and visualizations
- **Demos** - Showcase multiple app capabilities automatically

## Features

- **Flexible timing** - Each app can have a different display duration
- **Independent configs** - Each app uses its own saved configuration
- **Persistent** - Carousel settings are saved and restored on restart
- **Seamless rotation** - Apps switch automatically without API calls
- **Web UI support** - Configure carousel through the web interface

## Quick Start

### 1. Basic Carousel Setup

```python
import requests

API_BASE = "http://localhost:5000/api"

# Configure each app
requests.post(f"{API_BASE}/apps/clock/config", json={
    "color": [255, 0, 0]
})

requests.post(f"{API_BASE}/apps/scroll_text/config", json={
    "text": "Hello World!",
    "color": [0, 255, 0]
})

# Enable carousel
requests.post(f"{API_BASE}/carousel", json={
    "enabled": True,
    "apps": [
        {"app": "clock", "duration": 10},
        {"app": "scroll_text", "duration": 15}
    ]
})
```

### 2. Run the Example Script

```bash
# Make sure the server is running
python3 main.py

# In another terminal, run the example
python3 examples/carousel/carousel_example.py
```

The example will:
1. Configure three apps (clock, scroll_text, stars)
2. Enable carousel mode with 5s, 10s, and 8s durations
3. Monitor the rotation and display which app is showing
4. Disable carousel when you press Ctrl+C

## Using Carousel via API

### Enable Carousel

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

### Get Carousel Status

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

### Disable Carousel

```bash
curl -X POST http://localhost:5000/api/carousel \
  -H "Content-Type: application/json" \
  -d '{"enabled": false, "apps": []}'
```

## Using Carousel via Web Interface

1. Open the web interface: http://localhost:3000
2. Scroll to the "🔄 Carousel Mode" section
3. Click "Configure Carousel"
4. Check "Enable Carousel Mode"
5. Click "➕ Add App" for each app you want in the rotation
6. Select the app and set its duration (in seconds)
7. Click "Save Carousel"

The carousel will start immediately and rotate through your selected apps.

## Best Practices

### 1. Configure Apps First

Always configure each app's settings before adding it to the carousel:

```python
# Good: Configure first
configure_app("clock", {"color": [255, 0, 0]})
configure_app("stars", {"spawn_rate": 5})

# Then enable carousel
set_carousel(enabled=True, apps=[...])
```

### 2. Choose Appropriate Durations

- **Clock**: 5-10 seconds is usually enough
- **Scroll Text**: Base duration on text length (longer text = more time)
- **Stars/Animations**: 10-30 seconds for visual impact
- **Information**: 15-30 seconds for people to read

### 3. Test Before Deployment

```python
# Test with short durations first
test_apps = [
    {"app": "clock", "duration": 3},
    {"app": "scroll_text", "duration": 5}
]

# Then adjust to production durations
prod_apps = [
    {"app": "clock", "duration": 10},
    {"app": "scroll_text", "duration": 20}
]
```

### 4. Monitor and Adjust

Watch a full rotation cycle to ensure:
- Each app displays correctly
- Durations feel appropriate
- Transitions are smooth
- No apps crash or error

## Common Use Cases

### Information Display

```python
carousel_apps = [
    {"app": "clock", "duration": 10},           # Show time
    {"app": "scroll_text", "duration": 15},     # News headlines
    {"app": "temperature", "duration": 10},     # Weather
    {"app": "scroll_text", "duration": 15}      # Announcements
]
```

### Demo Mode

```python
carousel_apps = [
    {"app": "clock", "duration": 8},
    {"app": "scroll_text", "duration": 12},
    {"app": "stars", "duration": 10},
    {"app": "game_of_life", "duration": 15}
]
```

### Retail Display

```python
# Configure promotional messages
configure_app("scroll_text", {
    "text": "Sale! 50% off all items today!",
    "color": [255, 0, 0]
})

carousel_apps = [
    {"app": "scroll_text", "duration": 20},     # Promotion
    {"app": "clock", "duration": 5},            # Time check
    {"app": "qr_code", "duration": 15}          # QR for more info
]
```

## Troubleshooting

### Carousel Not Rotating

1. Check carousel is enabled:
   ```bash
   curl http://localhost:5000/api/carousel
   ```

2. Verify apps exist:
   ```bash
   curl http://localhost:5000/api/apps
   ```

3. Check server logs for errors

### Apps Not Configured Correctly

Each app in the carousel uses its saved configuration. Update it:

```bash
curl -X POST http://localhost:5000/api/apps/clock/config \
  -H "Content-Type: application/json" \
  -d '{"color": [255, 0, 0]}'
```

### Duration Not Working

- Durations are in **seconds** (not milliseconds)
- Minimum duration is technically 1 second
- Very short durations (<3s) may feel too fast
- Check for typos in the duration field

### Carousel Stuck on One App

This can happen if:
- Only one app is in the carousel
- The duration is very long
- An app crashed (check server logs)

Solution:
```bash
# Disable and re-enable carousel
curl -X POST http://localhost:5000/api/carousel \
  -d '{"enabled": false, "apps": []}'

curl -X POST http://localhost:5000/api/carousel \
  -d '{"enabled": true, "apps": [...]}'
```

## Advanced Topics

### Programmatic Carousel Updates

You can update the carousel while it's running:

```python
def update_carousel_schedule(time_of_day):
    if time_of_day == "morning":
        apps = [
            {"app": "clock", "duration": 10},
            {"app": "weather", "duration": 15}
        ]
    elif time_of_day == "evening":
        apps = [
            {"app": "clock", "duration": 5},
            {"app": "news", "duration": 20}
        ]
    
    set_carousel_config(enabled=True, apps=apps)
```

### Monitoring Carousel State

```python
def monitor_carousel():
    config = get_carousel_config()
    current_index = config['current_index']
    current_app = config['apps'][current_index]
    
    print(f"Currently showing: {current_app['app']}")
    print(f"Position: {current_index + 1}/{len(config['apps'])}")
```

## Related Documentation

- [API.md](../../docs/API.md) - Complete API reference
- [WEB_INTERFACE.md](../../docs/WEB_INTERFACE.md) - Web UI documentation
- [APPS.md](../../docs/APPS.md) - Creating custom apps

## Contributing

Have a great carousel example? Submit a PR with:
- A descriptive script name
- Clear comments explaining the use case
- Example output/screenshots
- Documentation updates