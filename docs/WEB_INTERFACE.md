# Web Interface Documentation

The RetroBoard Web Interface is a modern, user-friendly Vue 3 application that provides visual control over the LED matrix display.

## Overview

The web interface allows you to:
- Switch between available applications
- Configure app settings in real-time without interference
- Configure carousel mode to automatically rotate through apps
- View live connection status via WebSocket
- Control the display from any device on your network
- Toggle between dark and light themes
- Receive real-time updates without polling

## Architecture

### Technology Stack

- **Vue 3**: Modern reactive framework with Composition API
- **Vite**: Fast build tool and development server
- **Socket.IO Client**: WebSocket library for real-time communication
- **Vanilla CSS**: Simple, responsive styling without external dependencies

### Communication Flow

```
Browser (Port 3000)
    ↓ HTTP POST (Commands) + WebSocket (Real-time Updates)
Vite Dev Server (Port 3000)
    ↓ Proxy /api/* and WebSocket
Flask-SocketIO Server (Port 5000)
    ↓ Command Queue + Event Emission
Application Manager
    ↓ Controls + State Change Events
LED Matrix Driver
```

**Architecture:**
- **Commands** (switch app, update config) → REST API (POST)
- **Real-time updates** (app changes, settings) → WebSocket events
- **No polling** - Server pushes updates when state changes

## Installation

### Prerequisites

- Node.js 16+ or 18+
- pnpm package manager
- RetroBoard server running
- Python packages: `flask-socketio`, `python-socketio` (see requirements.txt)

### Setup

```bash
# Install Python dependencies (if not already done)
cd retroboard
pip install -r requirements.txt

# Install web dependencies
cd web
pnpm install
```

## Usage

### Development Mode

1. Start the RetroBoard server:
```bash
# In the main project directory
python3 server.py
```

2. Start the web development server:
```bash
# In the web directory
pnpm run dev
```

3. Open your browser to [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
cd web
pnpm run build
```

The built files will be in `web/dist/` and can be served by any static web server (nginx, Apache, etc.).

To preview the production build locally:
```bash
pnpm run preview
```

## Features

### Theme Toggle

Click the moon 🌙 or sun ☀️ button in the header to switch between dark and light themes. Your preference is automatically saved to browser local storage.

- **Dark Theme** (default): Easy on the eyes for extended use
- **Light Theme**: Traditional bright interface

### Carousel Mode

Carousel mode automatically rotates through multiple apps with configurable display times. This is perfect for:
- Information displays showing different data sources
- Digital signage cycling through messages
- Dashboards with multiple visualizations
- Showcasing different app capabilities

**Configuration:**
1. Click "Configure Carousel" to open the editor
2. Check "Enable Carousel Mode" to activate it
3. Click "➕ Add App" to add apps to the rotation
4. For each app:
   - Select which app to display
   - Set duration in seconds (how long to show it)
5. Click "Save Carousel" to apply

**Features:**
- Each app uses its saved configuration
- Duration is specified in seconds per app
- Apps can have different display times
- Carousel automatically loops back to the first app
- Configuration is saved and persists across server restarts
- Can be disabled without losing your app list

**Example Use Case:**
Show a clock for 10 seconds, scroll text for 15 seconds, and stars animation for 20 seconds, then repeat.

### Smooth Config Updates

When updating the configuration of the **currently running app**, the interface uses the `/api/config` endpoint to apply changes without restarting. This provides a seamless experience with no visual interruption.

- **Update Config** (same app): Uses `/api/config` - smooth, no restart
- **Switch to App** (different app): Uses `/api/switch` - restarts with new app

### App Switcher

The app switcher displays all available applications as cards. Click any card to select it and view its configuration options.

- **Active Indicator**: The currently running app is highlighted
- **Icons**: Each app has a distinctive emoji icon
- **Hover Effect**: Cards animate on hover for visual feedback

### Configuration Forms

Each app has its own configuration form that appears when selected:

#### Clock Configuration
- **Font Selection**: Choose between available BDF fonts
- **Color Picker**: RGB color values with visual preview

#### Scroll Text Configuration
- **Text Input**: Enter the message to display
- **Font Selection**: Choose font size
- **Speed Control**: Adjust scrolling speed (1-10)
- **FPS Control**: Set animation frame rate (10-60)
- **Color Picker**: RGB color values with visual preview

#### Stars Configuration
- **Spawn Rate**: Control how many stars appear per frame (1-10)
- **Lifetime**: Set how long stars last (10-100 frames)
- **FPS Control**: Set animation frame rate (10-120)

### Real-time Updates

The interface uses **WebSocket** for real-time bidirectional communication:
- Instantly notified when apps switch
- Immediate updates when settings change
- Live carousel rotation updates
- Automatic reconnection on network issues
- **No polling** - updates only when state changes

**How it works:**
1. Browser connects via WebSocket on page load
2. Server sends initial state immediately
3. Server pushes updates when state changes (app switch, config update, etc.)
4. Browser receives and displays updates in real-time

**Benefits:**
- Lower latency (no 2-second delay)
- Reduced server load (no constant polling)
- More efficient bandwidth usage
- Better user experience

### Manual State Refresh

Click the "🔄 Refresh" button next to "Stop App" to manually request the complete state from the server via WebSocket. Use this when:
- You want to ensure you have the latest state
- You suspect the connection may have missed an update
- You want to reset your local changes to match what's running
- Multiple users are controlling the display

Note: With WebSocket, manual refresh is rarely needed as updates arrive automatically.

### Connection Status

The header displays a live connection indicator:
- **Green dot**: Connected to server
- **Red dot**: Disconnected or server unreachable

## API Integration

The web interface uses a hybrid approach for optimal performance:

### REST API (Commands)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/apps` | GET | List available applications (initial load) |
| `/api/current` | GET | Get current app and configuration (fallback) |
| `/api/switch` | POST | Switch to a different app |
| `/api/stop` | POST | Stop the current app |
| `/api/config` | POST | Update app configuration |
| `/api/carousel` | GET | Get carousel configuration (initial load) |
| `/api/carousel` | POST | Update carousel configuration |
| `/api/settings` | POST | Update settings (brightness) |

### WebSocket Events (Real-time Updates)

| Event | Direction | Purpose |
|-------|-----------|---------|
| `connect` | Client → Server | Establish connection |
| `disconnect` | Client → Server | Connection lost |
| `request_state` | Client → Server | Request complete state |
| `apps_list` | Server → Client | Available apps and current app |
| `current_app` | Server → Client | App changed or config updated |
| `settings` | Server → Client | Settings changed (brightness) |
| `carousel_config` | Server → Client | Carousel configuration changed |

**Pattern:**
- **Commands**: Use REST POST endpoints
- **Updates**: Receive via WebSocket events
- **Initial load**: REST API for fallback, WebSocket for real-time

See [API.md](API.md) for complete API and WebSocket documentation.

## Configuration

### Development Server

The Vite development server is configured in `vite.config.js`:

```javascript
{
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
}
```

### API Proxy

In development mode, all `/api/*` requests are automatically proxied to `http://localhost:5000`. This avoids CORS issues and simplifies development.

For production deployment, you have two options:

1. **Serve from the same origin**: Host the static files on the same server as the API
2. **Configure CORS**: The Flask API already includes CORS support for cross-origin requests

## Deployment

### Option 1: Serve with Flask

You can serve the built web interface directly from the Flask server:

1. Build the web interface:
```bash
cd web
pnpm run build
```

2. Copy the `dist/` folder to a location accessible by Flask

3. Add a route to Flask to serve the static files (modify `api.py`):
```python
@app.route('/')
def index():
    return send_from_directory('path/to/dist', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('path/to/dist', path)
```

### Option 2: Separate Web Server

Use nginx or Apache to serve the static files:

**nginx example:**
```nginx
server {
    listen 80;
    server_name retroboard.local;

    # Serve static files
    location / {
        root /path/to/retroboard/web/dist;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 3: Remote Access

To access the web interface from other devices on your network:

1. Start the server with `--host 0.0.0.0`:
```bash
python3 server.py --host 0.0.0.0
```

2. Update `vite.config.js` to use your Raspberry Pi's IP:
```javascript
proxy: {
  '/api': {
    target: 'http://192.168.1.X:5000',  // Use your Pi's IP
    changeOrigin: true,
  }
}
```

3. Start the dev server with network access:
```bash
pnpm run dev -- --host
```

4. Access from any device: `http://<your-pi-ip>:3000`

## Customization

### Styling

The app uses scoped CSS in `App.vue` with full dark/light theme support.

**Light Theme Colors:**
- **Primary Color**: `#667eea` (purple)
- **Background**: Light gray gradient (`#e5e7eb` → `#d1d5db`)
- **Text**: Dark gray
- **Cards**: White

**Dark Theme Colors:**
- **Primary Color**: `#4b5563` (medium gray)
- **Background**: Black to dark gray gradient (`#111827` → `#1f2937`)
- **Text**: Light gray (`#e5e7eb`)
- **Cards**: Dark gray (`#1f2937`)

To customize, edit the `<style scoped>` section in `App.vue`. Theme is controlled via the `.dark-theme` class on the root element.

### Adding New Apps

When you add a new app to the RetroBoard server:

1. The app will automatically appear in the web interface
2. Add an icon mapping in `getAppIcon()`:
```javascript
function getAppIcon(app) {
  const icons = {
    clock: '🕐',
    scroll_text: '📜',
    stars: '✨',
    your_app: '🎨'  // Add your icon
  }
  return icons[app] || '📱'
}
```

3. Add a configuration form in the template:
```vue
<div v-else-if="selectedApp === 'your_app'" class="config-form">
  <!-- Your config inputs -->
</div>
```

4. Add a config ref:
```javascript
const yourAppConfig = ref({
  // default values
})
```

5. Update `getAppConfig()` to include your config.

## Troubleshooting

### Cannot connect to server

**Symptom**: Red "Disconnected" indicator, no apps shown

**Solutions**:
- Verify the RetroBoard server is running: `curl http://localhost:5000/api/health`
- Check the browser console for errors
- Ensure port 5000 is not blocked by firewall
- Verify CORS is enabled in `api.py`

### Configuration keeps resetting

**Symptom**: Form values change back while you're editing

**Solution**: This should no longer happen! The new version only polls for app name changes, not config. If you still see this:
- Clear browser cache and reload
- Check that you're using the latest version of App.vue

### Configuration not applying

**Symptom**: Changes in form don't affect the display

**Solutions**:
- Click "Switch to App" or "Update Config" button
- **Update Config** uses `/api/config` for smooth, instant updates (no restart)
- **Switch to App** uses `/api/switch` when changing apps (restarts the app)
- Check browser console for API errors
- Verify the server received the request (check server logs)
- Ensure values are within valid ranges
- Try clicking "🔄 Refresh" to sync with server

### Build fails

**Symptom**: `pnpm run build` errors

**Solutions**:
- Delete `node_modules/` and `pnpm-lock.yaml`, then run `pnpm install`
- Verify Node.js version is 16+
- Check for syntax errors in `App.vue`

### Proxy not working in development

**Symptom**: API requests fail with 404 or CORS errors

**Solutions**:
- Verify `vite.config.js` proxy configuration
- Ensure RetroBoard server is running on port 5000
- Check Vite dev server console for proxy errors
- Try accessing API directly: `http://localhost:5000/api/health`

## Browser Compatibility

The web interface is tested on:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

Modern browser features used:
- ES6+ JavaScript
- CSS Grid
- CSS Flexbox
- Fetch API

## Performance

- **Bundle Size**: ~60KB gzipped (production, includes Socket.IO client)
- **Initial Load**: <1s on modern browsers
- **Connection**: Persistent WebSocket (no polling overhead)
- **Memory Usage**: ~12MB typical (includes WebSocket connection)
- **Bandwidth**: Minimal - only updates when state changes

## Security Considerations

- **No authentication**: The current implementation has no authentication. If exposing to the internet, add authentication middleware.
- **Input validation**: All inputs are validated client-side, but server-side validation is also performed.
- **CORS**: Enabled for all origins (`*`) in development. Restrict in production.

## Future Enhancements

Planned features:
- [x] Dark mode toggle (implemented!)
- [x] Smart state management that doesn't interfere with editing (implemented!)
- [x] Carousel mode controls (implemented!)
- [x] WebSocket support for real-time updates without polling (implemented!)
- [ ] Enhanced visual color picker component (HTML5 color input)
- [ ] Live preview/thumbnail of display
- [ ] Preset management (save/load favorites)
- [ ] Keyboard shortcuts
- [ ] Schedule/timer interface
- [ ] Mobile app (PWA support)
- [ ] Authentication system
- [ ] Multi-user support with change notifications

## Development Tips

### Hot Module Replacement

Vite provides instant HMR. Changes to `App.vue` or `style.css` will update in the browser without a full reload.

Note: HMR will disconnect and reconnect the WebSocket automatically.

### Vue DevTools

Install the Vue DevTools browser extension for debugging:
- Inspect component state
- View reactive data
- Track API calls and WebSocket events
- Monitor performance
- View WebSocket connection status

### API Testing

Test API independently with curl:
```bash
# Health check
curl http://localhost:5000/api/health

# List apps
curl http://localhost:5000/api/apps

# Switch apps
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "clock"}'
```

## Contributing

When modifying the web interface:

1. Follow Vue 3 Composition API best practices
2. Keep components simple and focused
3. Use semantic HTML
4. Ensure responsive design
5. Test on multiple browsers
6. Update this documentation

## WebSocket Connection Details

### Connection Lifecycle

1. **Page Load**: Automatically connects to WebSocket
2. **Connected**: Server sends initial state (`apps_list`, `current_app`, `settings`, `carousel_config`)
3. **Running**: Receives updates as they happen
4. **Disconnected**: Automatically attempts to reconnect
5. **Reconnected**: Requests fresh state to resync

### Reconnection Strategy

Socket.IO handles reconnection automatically:
- Exponential backoff on connection failures
- Automatic retry with increasing intervals
- UI shows connection status (green/red dot)
- State resync on successful reconnection

### Development Tips

```javascript
// Check WebSocket status in browser console
socket.connected // true or false

// Manual state request
socket.emit('request_state')

// Listen to all events for debugging
socket.onAny((event, ...args) => {
  console.log('WebSocket event:', event, args);
});
```

## Related Documentation

- [README.md](../README.md) - Main project documentation
- [API.md](API.md) - Complete API and WebSocket reference
- [SERVER.md](SERVER.md) - Server configuration
- [APPS.md](APPS.md) - Creating custom applications
- [web/README.md](../web/README.md) - Web interface quick start