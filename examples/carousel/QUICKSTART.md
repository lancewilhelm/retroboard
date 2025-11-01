# Carousel Mode Quick Reference

## One-Minute Setup

```bash
# 1. Start the server
python3 main.py

# 2. Configure your apps
curl -X POST http://localhost:5000/api/apps/clock/config \
  -H "Content-Type: application/json" \
  -d '{"color": [255, 0, 0]}'

curl -X POST http://localhost:5000/api/apps/scroll_text/config \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World!", "color": [0, 255, 0]}'

# 3. Enable carousel
curl -X POST http://localhost:5000/api/carousel \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "apps": [
      {"app": "clock", "duration": 10},
      {"app": "scroll_text", "duration": 15}
    ]
  }'
```

Done! Your display will now rotate between apps.

## Quick Commands

### Enable Carousel
```bash
curl -X POST http://localhost:5000/api/carousel \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "apps": [{"app": "clock", "duration": 10}]}'
```

### Check Status
```bash
curl http://localhost:5000/api/carousel
```

### Disable Carousel
```bash
curl -X POST http://localhost:5000/api/carousel \
  -H "Content-Type: application/json" \
  -d '{"enabled": false, "apps": []}'
```

## Python Example

```python
import requests

API = "http://localhost:5000/api"

# Enable carousel with 3 apps
requests.post(f"{API}/carousel", json={
    "enabled": True,
    "apps": [
        {"app": "clock", "duration": 10},
        {"app": "scroll_text", "duration": 15},
        {"app": "stars", "duration": 20}
    ]
})

# Check status
status = requests.get(f"{API}/carousel").json()
print(status)

# Disable
requests.post(f"{API}/carousel", json={"enabled": False, "apps": []})
```

## Web Interface

1. Open http://localhost:3000
2. Scroll to "🔄 Carousel Mode"
3. Click "Configure Carousel"
4. Check "Enable Carousel Mode"
5. Add apps with "➕ Add App"
6. Set duration for each app
7. Click "Save Carousel"

## Tips

- **Durations are in seconds**
- **Each app uses its saved config**
- **Configure apps before adding to carousel**
- **Carousel persists across restarts**
- **Clock**: 5-10s | **Text**: 10-20s | **Animations**: 15-30s

## Common Patterns

### Information Display
- Clock (10s) → Weather (15s) → News (20s)

### Demo Mode
- Show all apps for 8-10 seconds each

### Signage
- Main message (20s) → Clock (5s) → QR code (15s)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Not rotating | Check `enabled: true` and app names |
| Wrong config | Update with `/api/apps/<name>/config` |
| Too fast/slow | Adjust duration values |
| Stuck | Disable and re-enable carousel |

## Full Documentation

- [README.md](README.md) - Complete examples
- [API.md](../../docs/API.md) - API reference
- [WEB_INTERFACE.md](../../docs/WEB_INTERFACE.md) - Web UI guide