# Matrix Application Server

## Overview

The Matrix Application Server provides a simple, extensible framework for running and controlling LED matrix applications through an HTTP API.

## Architecture

### Components

1. **MatrixApplication** (`apps/base.py`)
   - Abstract base class for all applications
   - Defines lifecycle: setup() → loop() → cleanup()
   - Simple, single-frame iteration model

2. **ApplicationManager** (`manager.py`)
   - Manages application lifecycle
   - Handles switching between apps
   - Processes commands from API
   - Runs in main thread

3. **API Server** (`api.py`)
   - Flask-based HTTP REST API
   - Runs in separate thread
   - Communicates via thread-safe queue
   - Provides remote control

4. **Applications** (`apps/`)
   - `ClockApp` - Digital clock
   - `ScrollTextApp` - Scrolling text
   - `StarsApp` - Twinkling stars

## How It Works

### Application Lifecycle

```
1. App is created: __init__(driver, config)
2. App setup: setup()
3. Loop runs repeatedly: loop() → loop() → loop()...
4. App stops: cleanup()
```

Each `loop()` call draws one frame. The manager calls it repeatedly.

### Thread Model

```
Main Thread:                API Thread:
  ApplicationManager          Flask Server
       ↓                           ↓
  while running:              Handle requests
    Check queue                    ↓
    Process commands          Put commands
    Call app.loop()           in queue
    Sleep briefly                  ↓
                              Return response
```

Communication happens through a thread-safe `queue.Queue`.

### Command Flow

```
User → HTTP Request → API Server → Queue → Manager → Application

Example:
curl POST /api/switch → Flask → queue.put() → manager.process_commands() → switch_app()
```

## File Structure

```
retroboard/
├── apps/                    # Application implementations
│   ├── __init__.py
│   ├── base.py             # MatrixApplication base class
│   ├── clock.py            # ClockApp
│   ├── scroll_text.py      # ScrollTextApp
│   └── stars.py            # StarsApp
├── manager.py              # ApplicationManager
├── api.py                  # Flask API server
├── server.py               # Main entry point
├── test_api.py             # API test suite
└── API.md                  # API documentation
```

## Usage

### Starting the Server

```bash
# Simulated display
python3 server.py

# With hardware
sudo python3 server.py --hardware

# Custom settings
python3 server.py --width 128 --height 64 --port 8080 --app stars
```

### Using the API

```bash
# List apps
curl http://localhost:5000/api/apps

# Switch apps
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "scroll_text", "config": {"text": "Hello!"}}'

# Stop current app
curl -X POST http://localhost:5000/api/stop
```

See [API.md](API.md) for complete documentation.

## Creating New Applications

### Minimal Example

```python
from apps.base import MatrixApplication
import time

class MyApp(MatrixApplication):
    def setup(self):
        # Initialize once
        self.canvas = self.driver.create_frame_canvas()
        self.x = 0
    
    def loop(self):
        # Draw one frame
        self.canvas.clear()
        self.canvas.set_pixel(self.x, 10, 255, 0, 0)
        self.canvas = self.driver.update(self.canvas)
        
        self.x = (self.x + 1) % self.driver.get_width()
        time.sleep(0.05)
    
    # cleanup() is optional, inherits default clear()
```

### Register and Use

```python
# In server.py
from apps.myapp import MyApp

manager.register_app('myapp', MyApp)
```

```bash
# Via API
curl -X POST http://localhost:5000/api/switch \
  -d '{"app": "myapp"}'
```

## Configuration System

Each app can accept configuration:

```python
class MyApp(MatrixApplication):
    def setup(self):
        # Read from self.config
        self.speed = self.config.get('speed', 1)
        self.color = self.config.get('color', (255, 0, 0))
    
    def update_config(self, key, value):
        # Handle live config updates
        super().update_config(key, value)
        if key == 'speed':
            self.speed = value
```

Usage:

```bash
# Set initial config
curl -X POST http://localhost:5000/api/switch \
  -d '{"app": "myapp", "config": {"speed": 5}}'

# Update while running
curl -X POST http://localhost:5000/api/config \
  -d '{"speed": 10}'
```

## Error Handling

The system is designed to be resilient:

- **App crashes**: Manager catches exceptions, stops crashed app
- **Invalid requests**: API returns proper error codes
- **Graceful shutdown**: Ctrl+C stops everything cleanly

## Testing

```bash
# Run test suite
python3 test_api.py

# Manual testing
python3 server.py
# In another terminal:
curl http://localhost:5000/api/apps
```

## Future Enhancements

Planned features:

1. **Carousel Mode**
   - Auto-rotate through apps
   - Configurable duration per app

2. **Scheduling**
   - Run different apps at different times
   - Cron-like scheduling

3. **Presets**
   - Save favorite configurations
   - Quick switch via names

4. **WebSocket Support**
   - Real-time updates
   - Live status streaming

5. **Web UI**
   - Browser-based control panel
   - Visual app switcher

6. **Transitions**
   - Fade between apps
   - Custom transition effects

## Design Philosophy

### Keep It Simple

- Apps just implement `loop()` - one frame at a time
- No complex threading in apps
- Configuration is just a dictionary
- Standard HTTP/REST interface

### Make It Extensible

- Easy to add new apps (inherit base class)
- Config system built-in from start
- Clear separation of concerns
- Room to grow without breaking changes

### Stay Lean

- ~500 lines of core code
- Minimal dependencies (Flask only)
- No overengineering
- Start simple, add complexity as needed

## Tips

### Debugging Apps

Add logging:
```python
import logging
logger = logging.getLogger(__name__)

class MyApp(MatrixApplication):
    def loop(self):
        logger.info(f"Drawing frame at x={self.x}")
        # ...
```

### Long Operations

Check `should_stop()`:
```python
def loop(self):
    for i in range(100):
        if self.should_stop():
            break
        # do work
```

### State Management

Use instance variables:
```python
def setup(self):
    self.stars = []
    self.counter = 0

def loop(self):
    self.counter += 1
    # Use self.stars, self.counter
```

## Summary

The Matrix Application Server provides:
- ✅ Simple application framework
- ✅ HTTP API for remote control
- ✅ Clean separation of concerns
- ✅ Easy to extend
- ✅ Production-ready error handling
- ✅ Well documented

Start the server, make API calls, build new apps!
