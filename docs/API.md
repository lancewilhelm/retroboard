# Matrix Server API Documentation

The Matrix Server provides an HTTP API for controlling LED matrix applications.

## Starting the Server

### Basic Usage
```bash
# Run with simulated display (no hardware needed)
python3 server.py

# Run with hardware
sudo python3 server.py --hardware

# Custom display size
python3 server.py --width 128 --height 64

# Start with different app
python3 server.py --app stars

# Custom port
python3 server.py --port 8080
```

### Command Line Options
- `--hardware` - Use real LED matrix hardware
- `--rows N` - Matrix rows (hardware mode, default: 32)
- `--cols N` - Matrix columns (hardware mode, default: 64)
- `--width N` - Display width (simulated mode, default: 64)
- `--height N` - Display height (simulated mode, default: 32)
- `--port N` - API server port (default: 5000)
- `--host IP` - API server host (default: 0.0.0.0)
- `--app NAME` - Initial app to run (default: clock)

## API Endpoints

### List Available Apps
```bash
GET /api/apps
```

**Response:**
```json
{
  "apps": ["clock", "scroll_text", "stars"],
  "current": "clock"
}
```

### Get Current App Info
```bash
GET /api/current
```

**Response:**
```json
{
  "app": "clock",
  "config": {
    "font": "6x10",
    "color": [0, 255, 255]
  }
}
```

### Switch Applications
```bash
POST /api/switch
Content-Type: application/json

{
  "app": "scroll_text",
  "config": {
    "text": "Hello World!",
    "color": [255, 0, 0],
    "speed": 2
  }
}
```

**Response:**
```json
{
  "success": true,
  "app": "scroll_text"
}
```

### Stop Current App
```bash
POST /api/stop
```

**Response:**
```json
{
  "success": true
}
```

### Update App Configuration
```bash
POST /api/config
Content-Type: application/json

{
  "color": [255, 0, 0],
  "speed": 3
}
```

**Response:**
```json
{
  "success": true
}
```

### Health Check
```bash
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "manager_running": true,
  "current_app": "clock"
}
```

## Usage Examples

### Using curl

```bash
# List apps
curl http://localhost:5000/api/apps

# Switch to clock
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "clock"}'

# Switch to scrolling text with custom message
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "scroll_text", "config": {"text": "Hello LED Matrix!"}}'

# Switch to stars with custom settings
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "stars", "config": {"spawn_rate": 3, "lifetime": 60}}'

# Update current app color
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"color": [255, 0, 0]}'

# Stop current app (blank display)
curl -X POST http://localhost:5000/api/stop

# Check health
curl http://localhost:5000/api/health
```

### Using Python requests

```python
import requests

# Switch to clock
response = requests.post('http://localhost:5000/api/switch', json={
    'app': 'clock',
    'config': {'color': [0, 255, 0]}
})
print(response.json())

# Update scroll text
requests.post('http://localhost:5000/api/switch', json={
    'app': 'scroll_text',
    'config': {
        'text': 'Python is awesome!',
        'speed': 2,
        'color': [255, 255, 0]
    }
})
```

## Application Configurations

### Clock App
```json
{
  "app": "clock",
  "config": {
    "font": "6x10",
    "color": [0, 255, 255]
  }
}
```

Options:
- `font` - Path to BDF font file
- `color` - RGB tuple [r, g, b] (0-255 each)

### Scroll Text App
```json
{
  "app": "scroll_text",
  "config": {
    "text": "Hello World!",
    "font": "6x10",
    "color": [0, 255, 255],
    "speed": 1,
    "fps": 30
  }
}
```

Options:
- `text` - Text to display
- `font` - Path to BDF font file
- `color` - RGB tuple [r, g, b]
- `speed` - Scroll speed in pixels per frame (default: 1)
- `fps` - Frames per second (default: 30)

### Stars App
```json
{
  "app": "stars",
  "config": {
    "spawn_rate": 1,
    "lifetime": 40,
    "fps": 60
  }
}
```

Options:
- `spawn_rate` - Stars spawned per frame (default: 1)
- `lifetime` - How many frames a star lives (default: 40)
- `fps` - Frames per second (default: 60)

## Testing the API

A simple test script is provided:

```bash
python3 test_api.py
```

This will:
1. Start the server (simulated mode)
2. Test all API endpoints
3. Switch between apps
4. Verify responses

## Error Handling

### App Not Found (404)
```bash
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "nonexistent"}'
```

Response:
```json
{
  "error": "App not found"
}
```

### Missing Parameters (400)
```bash
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response:
```json
{
  "error": "Missing app name"
}
```

## Future Enhancements

Planned features:
- Carousel mode (auto-rotate through apps)
- Scheduling (run different apps at different times)
- Presets (save favorite configurations)
- WebSocket support for real-time updates
- Web UI for visual control
