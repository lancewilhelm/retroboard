# RetroBoard Web Controller

A simple Vue 3 web application for controlling the RetroBoard LED matrix display.

## Features

- 🎮 Control the LED matrix from your browser
- 🔄 Switch between available applications (clock, scroll_text, stars)
- ⚙️ Configure app settings in real-time
- 🎨 Color picker for RGB values
- 📊 Live connection status
- 🔴 Stop running applications
- 🌓 Dark/Light theme toggle
- 🔄 Manual config refresh (no auto-polling interference)

## Prerequisites

- Node.js 16+ or 18+
- pnpm package manager
- RetroBoard server running (see main project README)

## Installation

1. Navigate to the web directory:
```bash
cd web
```

2. Install dependencies:
```bash
pnpm install
```

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

The web app will automatically proxy API requests to the RetroBoard server running on port 5000.

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

**Note:** The interface monitors which app is running but does NOT automatically overwrite your config changes. Edit freely without interference!

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

If an app is already running, modify its configuration and click "Update Config" to apply changes **smoothly without restarting the app**. The interface intelligently uses the `/api/config` endpoint to update settings on-the-fly, preventing any jarring visual interruption.

**Refresh Config:** Click the "🔄 Refresh" button to reload the current configuration from the server. This is useful if:
- You switched apps via the API/curl and want to see the server's config
- You want to reset your local changes to match what's running
- Another user changed the config

### Stopping Apps

Click the "Stop App" button to clear the display and stop the current application.

## Architecture

- **Vue 3**: Modern reactive framework with Composition API
- **Vite**: Fast build tool and dev server
- **API Proxy**: Development server proxies `/api` requests to port 5000

## Troubleshooting

### Cannot connect to server
- Ensure the RetroBoard server is running on port 5000
- Check that the server is accessible at `http://localhost:5000/api/health`

### App not updating
- The web interface polls for the current app name every 2 seconds
- Config is NOT auto-refreshed to prevent overwriting your edits
- Click "🔄 Refresh" to manually reload config from server
- Check browser console for errors
- Verify the server is responding to API requests

### Configuration not applying
- Make sure you click "Switch to App" or "Update Config" after changing values
- **Update Config** uses `/api/config` for smooth updates (no restart)
- **Switch to App** uses `/api/switch` when changing apps (restarts app)
- Color values must be integers between 0-255
- Speed and FPS values have minimum/maximum limits

## API Endpoints Used

The web app communicates with these RetroBoard API endpoints:

- `GET /api/apps` - List available applications
- `GET /api/current` - Get current app and config
- `POST /api/switch` - Switch to a different app
- `POST /api/stop` - Stop current app
- `POST /api/config` - Update app configuration

See the main project's `docs/API.md` for full API documentation.

## Future Enhancements

Potential improvements:
- ✅ Dark mode toggle (implemented!)
- WebSocket support for real-time updates
- Preset configurations (save/load favorites)
- Enhanced color picker UI component
- Preview/thumbnail of running app
- Keyboard shortcuts
- Carousel mode controls
- Schedule/timer functionality
- Multi-user change notifications