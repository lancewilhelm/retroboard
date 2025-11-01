# Matrix Server API Documentation

The Matrix Server provides an HTTP REST API and WebSocket support for controlling LED matrix applications in real-time.

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

### Get App Configuration
```bash
GET /api/apps/<app_name>/config
```

**Response:**
```json
{
  "app": "scroll_text",
  "config": {
    "text": "Hello World!",
    "color": [255, 0, 0],
    "speed": 2
  }
}
```

### Update App Configuration
```bash
POST /api/apps/<app_name>/config
Content-Type: application/json

{
  "color": [255, 0, 0],
  "speed": 3
}
```

**Response:**
```json
{
  "success": true,
  "app": "scroll_text"
}
```

**Note:** This endpoint saves configuration for any app (current or not). If updating the current running app, changes are applied immediately without restart.

### Update Current App Configuration (Legacy)
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

**Note:** This endpoint is maintained for backwards compatibility. Use `POST /api/apps/<app_name>/config` for new implementations.

### Get Settings
```bash
GET /api/settings
```

**Response:**
```json
{
  "brightness": 75
}
```

### Update Settings
```bash
POST /api/settings
Content-Type: application/json

{
  "brightness": 50
}
```

**Response:**
```json
{
  "success": true
}
```

**Settings:**
- `brightness` - Display brightness (0-100, default: 100)

**Note:** Settings are persisted to `state.json` and restored on server restart.

### Get Carousel Configuration
```bash
GET /api/carousel
```

**Response:**
```json
{
  "enabled": true,
  "apps": [
    {"app": "clock", "duration": 10},
    {"app": "scroll_text", "duration": 15},
    {"app": "stars", "duration": 20}
  ],
  "current_index": 0
}
```

### Update Carousel Configuration
```bash
POST /api/carousel
Content-Type: application/json

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
  "apps": [
    {"app": "clock", "duration": 10},
    {"app": "scroll_text", "duration": 15},
    {"app": "stars", "duration": 20}
  ]
}
```

**Carousel Settings:**
- `enabled` - Boolean, whether carousel mode is active
- `apps` - Array of app configurations to rotate through
  - `app` - Name of the app to display
  - `duration` - Time in seconds to display this app before switching to the next

**Notes:**
- When carousel is enabled, it automatically rotates through the specified apps
- Each app uses its saved configuration from `/api/apps/<app_name>/config`
- The carousel index wraps around (after the last app, it goes back to the first)
- Carousel configuration is persisted to `state.json`
- Setting `enabled: false` stops the carousel and maintains the current app
- Duration must be a positive number (in seconds)

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

## WebSocket Support

The server provides real-time WebSocket communication for instant updates without polling.

### Connection

Connect to the WebSocket endpoint at the same host and port as the REST API:

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000');
```

### Client Events (Emitted by Client)

#### connect
Automatically emitted when connection is established. Server responds with initial state.

#### disconnect
Automatically emitted when connection is lost.

#### request_state
Request complete current state from server.

```javascript
socket.emit('request_state');
```

### Server Events (Received by Client)

#### apps_list
List of available apps and current app.

```javascript
socket.on('apps_list', (data) => {
  console.log('Apps:', data.apps);
  console.log('Current:', data.current);
});
```

**Data:**
```json
{
  "apps": ["clock", "scroll_text", "stars"],
  "current": "clock"
}
```

#### current_app
Current app name and configuration. Emitted when app switches or config changes.

```javascript
socket.on('current_app', (data) => {
  console.log('App:', data.app);
  console.log('Config:', data.config);
});
```

**Data:**
```json
{
  "app": "clock",
  "config": {
    "font": "tom-thumb",
    "color": [255, 0, 0]
  }
}
```

#### settings
Global settings changes (brightness, etc.).

```javascript
socket.on('settings', (data) => {
  console.log('Brightness:', data.brightness);
});
```

**Data:**
```json
{
  "brightness": 75
}
```

#### carousel_config
Carousel configuration updates.

```javascript
socket.on('carousel_config', (data) => {
  console.log('Enabled:', data.enabled);
  console.log('Apps:', data.apps);
});
```

**Data:**
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

### WebSocket Example

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to RetroBoard');
  socket.emit('request_state');
});

socket.on('current_app', (data) => {
  console.log(`Now showing: ${data.app}`);
});

socket.on('settings', (data) => {
  console.log(`Brightness: ${data.brightness}%`);
});

socket.on('carousel_config', (data) => {
  if (data.enabled) {
    console.log(`Carousel active with ${data.apps.length} apps`);
  }
});
```

### Benefits of WebSocket

- **Real-time updates** - No polling required
- **Lower latency** - Instant notification of changes
- **Reduced bandwidth** - Only send data when needed
- **Bidirectional** - Server can push updates to clients
- **Efficient** - Persistent connection eliminates HTTP overhead

### REST + WebSocket Pattern

Use REST endpoints for commands (POST/PUT) and WebSocket for real-time state updates:

```javascript
// Send commands via REST
await fetch('/api/switch', {
  method: 'POST',
  body: JSON.stringify({ app: 'clock' })
});

// Receive updates via WebSocket
socket.on('current_app', (data) => {
  // Update UI immediately
});
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

# Switch to stars (uses saved config)
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "stars"}'

# Get saved config for an app
curl http://localhost:5000/api/apps/scroll_text/config

# Save config for an app (without switching to it)
curl -X POST http://localhost:5000/api/apps/scroll_text/config \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello LED!", "color": [255, 0, 0], "speed": 2}'

# Update current app color (applies immediately)
curl -X POST http://localhost:5000/api/apps/clock/config \
  -H "Content-Type: application/json" \
  -d '{"color": [255, 0, 0]}'

# Stop current app (blank display)
curl -X POST http://localhost:5000/api/stop

# Check health
curl http://localhost:5000/api/health

# Get settings
curl http://localhost:5000/api/settings

# Update brightness
curl -X POST http://localhost:5000/api/settings \
  -H "Content-Type: application/json" \
  -d '{"brightness": 50}'

# Get carousel configuration
curl http://localhost:5000/api/carousel

# Enable carousel mode
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

# Disable carousel mode
curl -X POST http://localhost:5000/api/carousel \
  -H "Content-Type: application/json" \
  -d '{"enabled": false, "apps": []}'
```

### Using Python requests

```python
import requests

# Get saved config for an app
response = requests.get('http://localhost:5000/api/apps/clock/config')
print(response.json())

# Pre-configure scroll_text (without switching to it)
requests.post('http://localhost:5000/api/apps/scroll_text/config', json={
    'text': 'Python is awesome!',
    'speed': 2,
    'color': [255, 255, 0]
})

# Now switch to it (uses saved config)
requests.post('http://localhost:5000/api/switch', json={
    'app': 'scroll_text'
})

# Update current app color immediately
requests.post('http://localhost:5000/api/apps/scroll_text/config', json={
    'color': [0, 255, 0]
})

# Get settings
response = requests.get('http://localhost:5000/api/settings')
print(response.json())

# Update brightness
requests.post('http://localhost:5000/api/settings', json={
    'brightness': 75
})

# WebSocket example
import socketio

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to RetroBoard')
    sio.emit('request_state')

@sio.on('current_app')
def on_current_app(data):
    print(f"Now showing: {data['app']}")

@sio.on('settings')
def on_settings(data):
    print(f"Brightness: {data['brightness']}%")

sio.connect('http://localhost:5000')
sio.wait()
```

# Get carousel configuration
response = requests.get('http://localhost:5000/api/carousel')
print(response.json())

# Enable carousel mode with multiple apps
requests.post('http://localhost:5000/api/carousel', json={
    'enabled': True,
    'apps': [
        {'app': 'clock', 'duration': 10},
        {'app': 'scroll_text', 'duration': 15},
        {'app': 'stars', 'duration': 20}
    ]
})

# Disable carousel mode
requests.post('http://localhost:5000/api/carousel', json={
    'enabled': False,
    'apps': []
})
```

## RESTful API Design

The API follows RESTful principles for configuration management:

- **GET /api/apps/<app_name>/config** - Retrieve saved configuration
- **POST /api/apps/<app_name>/config** - Save/update configuration
- **POST /api/switch** - Switch to app (uses saved config)

### Benefits

1. **Pre-configure apps** - Set up apps before switching to them
2. **Persistent configs** - All configs are automatically saved to `state.json`
3. **Immediate updates** - Updating current app applies changes instantly
4. **Independent operations** - Configure one app while another is running

### Workflow Example

```bash
# 1. Configure multiple apps without switching
curl -X POST http://localhost:5000/api/apps/clock/config \
  -d '{"color": [255, 0, 0]}'
curl -X POST http://localhost:5000/api/apps/stars/config \
  -d '{"spawn_rate": 5}'

# 2. Switch between them (each uses its saved config)
curl -X POST http://localhost:5000/api/switch -d '{"app": "clock"}'
curl -X POST http://localhost:5000/api/switch -d '{"app": "stars"}'

# 3. Both apps remember their settings across switches!
```

## Application Configurations

### Clock App

**Set configuration:**
```bash
POST /api/apps/clock/config
{
  "font": "6x10",
  "color": [0, 255, 255]
}
```

Options:
- `font` - Path to BDF font file
- `color` - RGB tuple [r, g, b] (0-255 each)

### Scroll Text App

**Set configuration:**
```bash
POST /api/apps/scroll_text/config
{
  "text": "Hello World!",
  "font": "6x10",
  "color": [0, 255, 255],
  "speed": 1,
  "fps": 30
}
```

Options:
- `text` - Text to display
- `font` - Path to BDF font file
- `color` - RGB tuple [r, g, b]
- `speed` - Scroll speed in pixels per frame (default: 1)
- `fps` - Frames per second (default: 30)

### Stars App

**Set configuration:**
```bash
POST /api/apps/stars/config
{
  "spawn_rate": 1,
  "lifetime": 40,
  "fps": 60
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

## Carousel Mode

Carousel mode allows you to automatically rotate through multiple apps with configurable display times.

### How It Works

1. **Configure Apps** - Set up each app's configuration separately
2. **Enable Carousel** - Specify which apps to rotate through and for how long
3. **Auto-Rotation** - The server automatically switches apps after each duration

### Example Workflow

```bash
# 1. Configure each app
curl -X POST http://localhost:5000/api/apps/clock/config \
  -H "Content-Type: application/json" \
  -d '{"color": [255, 0, 0]}'

curl -X POST http://localhost:5000/api/apps/scroll_text/config \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World!", "color": [0, 255, 0]}'

curl -X POST http://localhost:5000/api/apps/stars/config \
  -H "Content-Type: application/json" \
  -d '{"spawn_rate": 3}'

# 2. Enable carousel mode
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

# The display will now show:
# - Clock for 10 seconds (in red)
# - Scroll text for 15 seconds (in green, saying "Hello World!")
# - Stars for 20 seconds (with spawn rate of 3)
# - Then repeat from clock
```

### Carousel Features

- **Persistent** - Carousel configuration is saved to `state.json`
- **Seamless** - Apps switch automatically without API calls
- **Flexible** - Each app can have different display durations
- **Independent** - Each app uses its own saved configuration
- **Controllable** - Can be enabled/disabled via API or web interface

## Future Enhancements

Planned features:
- Scheduling (run different apps at different times)
- Presets (save favorite configurations)
- Enhanced WebSocket events (app lifecycle, errors, logs)
- WebSocket support for real-time updates
