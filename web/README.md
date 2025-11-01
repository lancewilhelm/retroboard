# RetroBoard Web Controller

A simple Vue 3 web application for controlling the RetroBoard LED matrix display.

## Features

- 🎮 Control the LED matrix from your browser
- 🔄 Switch between available applications (clock, scroll_text, stars)
- ⚙️ Configure app settings in real-time
- 🎨 Color picker for RGB values
- 📊 Live connection status via WebSocket
- 🔴 Stop running applications
- 🌓 Dark/Light theme toggle
- ⚡ Real-time updates without polling
- 🔄 Carousel mode for automatic app rotation

## Prerequisites

- Node.js 16+ or 18+
- pnpm package manager
- RetroBoard server running with WebSocket support (see main project README)

## Installation

1. Install Python dependencies (if not already done):
```bash
cd retroboard
pip install -r requirements.txt
```

This installs Flask-SocketIO for WebSocket support.

2. Navigate to the web directory and install dependencies:
```bash
cd web
pnpm install
```

This installs Vue 3 and Socket.IO client.

## Development

1. Start the RetroBoard server (in the main project directory):
```bash
# With simulated display
python3 server.py

# Or with hardware
sudo python3 server.py --hardware
```

2. In a separate terminal, start the web development server:
```bash
cd web
pnpm run dev
```

3. Open your browser to [http://localhost:3000](http://localhost:3000)

The web app will automatically:
- Proxy API requests to the RetroBoard server running on port 5000
- Connect to WebSocket for real-time updates

## Building for Production

Build the static files:
```bash
pnpm run build
```

The built files will be in the `dist/` directory and can be served by any static web server.

Preview the production build:
```bash
pnpm run preview
```

## Usage

### Theme Toggle

Click the moon 🌙 or sun ☀️ icon in the header to switch between dark and light themes. Your preference is saved in browser storage.

### Switching Apps

1. Click on any app card to select it
2. Configure the app settings in the form below
3. Click "Switch to App" to activate it

**Note:** The interface uses WebSocket to receive real-time updates but does NOT automatically overwrite your config changes. Edit freely without interference!

### Configuring Apps

#### Clock
- **Font**: Choose between tom-thumb or 6x10
- **Color**: RGB values (0-255 for each channel)

#### Scroll Text
- **Text**: The message to display
- **Font**: Choose between tom-thumb or 6x10
- **Speed**: Scroll speed in pixels per frame (1-10)
- **FPS**: Animation frame rate (10-60)
- **Color**: RGB values (0-255 for each channel)

#### Stars
- **Spawn Rate**: Number of stars per frame (1-10)
- **Lifetime**: How long stars last in frames (10-100)
- **FPS**: Animation frame rate (10-120)

### Updating Running App

If an app is already running, modify its configuration and click "Update Config" to apply changes **smoothly without restarting the app**. The interface intelligently uses the `/api/config` endpoint to update settings on-the-fly, preventing any jarring visual interruption. Updates are confirmed instantly via WebSocket.

**Refresh State:** Click the "🔄 Refresh" button to request the complete current state from the server via WebSocket. This is useful if:
- You want to ensure you have the latest state
- You suspect a WebSocket update may have been missed
- Multiple users are controlling the display

Note: With WebSocket, manual refresh is rarely needed as updates arrive automatically in real-time.

### Stopping Apps

Click the "Stop App" button to clear the display and stop the current application.

## Architecture

- **Vue 3**: Modern reactive framework with Composition API
- **Vite**: Fast build tool and dev server
- **Socket.IO Client**: WebSocket library for real-time communication
- **API Proxy**: Development server proxies `/api` requests and WebSocket to port 5000

### Communication Pattern

- **Commands** (switch app, update config) → REST API POST requests
- **Real-time updates** (app changes, settings) → WebSocket events
- **No polling** - Server pushes updates when state changes

## Troubleshooting

### Cannot connect to server
- Ensure the RetroBoard server is running on port 5000
- Check that the server is accessible at `http://localhost:5000/api/health`
- Verify WebSocket connection in browser console: "WebSocket connected"
- Check server logs for "Client connected via WebSocket"

### App not updating
- Check the connection indicator (should be green)
- Open browser console and look for WebSocket errors
- Verify the server has `flask-socketio` installed
- Click "🔄 Refresh" to manually request state update
- WebSocket automatically reconnects if disconnected

### Configuration not applying
- Make sure you click "Switch to App" or "Update Config" after changing values
- **Update Config** uses `/api/config` for smooth updates (no restart)
- **Switch to App** uses `/api/switch` when changing apps (restarts app)
- Color values must be integers between 0-255
- Speed and FPS values have minimum/maximum limits

## Communication

The web app uses a hybrid REST + WebSocket approach:

### REST API (Commands)
- `GET /api/apps` - List available applications (initial load)
- `POST /api/switch` - Switch to a different app
- `POST /api/stop` - Stop current app
- `POST /api/config` - Update app configuration
- `POST /api/carousel` - Update carousel configuration
- `POST /api/settings` - Update settings (brightness)

### WebSocket Events (Real-time Updates)
- `current_app` - App changed or config updated
- `apps_list` - Available apps list
- `settings` - Settings changed
- `carousel_config` - Carousel configuration updated

See the main project's `docs/API.md` for full API and WebSocket documentation.

## Future Enhancements

Potential improvements:
- ✅ Dark mode toggle (implemented!)
- ✅ WebSocket support for real-time updates (implemented!)
- ✅ Carousel mode controls (implemented!)
- Preset configurations (save/load favorites)
- Enhanced color picker UI component
- Preview/thumbnail of running app
- Keyboard shortcuts
- Schedule/timer functionality
- Enhanced WebSocket events (logs, errors)