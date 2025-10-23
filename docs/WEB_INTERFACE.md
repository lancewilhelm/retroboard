# Web Interface Documentation

The RetroBoard Web Interface is a modern, user-friendly Vue 3 application that provides visual control over the LED matrix display.

## Overview

The web interface allows you to:
- Switch between available applications
- Configure app settings in real-time without interference
- View live connection status
- Control the display from any device on your network
- Toggle between dark and light themes

## Architecture

### Technology Stack

- **Vue 3**: Modern reactive framework with Composition API
- **Vite**: Fast build tool and development server
- **Vanilla CSS**: Simple, responsive styling without external dependencies

### Communication Flow

```
Browser (Port 3000)
    ↓ HTTP Requests
Vite Dev Server (Port 3000)
    ↓ Proxy /api/* requests
Flask API Server (Port 5000)
    ↓ Command Queue
Application Manager
    ↓ Controls
LED Matrix Driver
```

## Installation

### Prerequisites

- Node.js 16+ or 18+
- pnpm package manager
- RetroBoard server running

### Setup

```bash
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

The interface intelligently polls the API every 2 seconds to:
- Monitor which app is currently running
- Detect if the app was changed externally (via API or curl)
- Check connection health

**Important:** Configuration values are NOT automatically refreshed during polling. This prevents the interface from overwriting your edits while you're configuring an app.

### Manual Config Refresh

Click the "🔄 Refresh" button next to "Stop App" to manually reload the current configuration from the server. Use this when:
- You switched apps via the API and want to see the server's config
- You want to reset your local changes to match what's running
- Another user/client changed the config
- You suspect the config is out of sync

### Connection Status

The header displays a live connection indicator:
- **Green dot**: Connected to server
- **Red dot**: Disconnected or server unreachable

## API Integration

The web interface communicates with the RetroBoard server through these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/apps` | GET | List available applications |
| `/api/current` | GET | Get current app and configuration |
| `/api/switch` | POST | Switch to a different app |
| `/api/stop` | POST | Stop the current app |
| `/api/config` | POST | Update app configuration |
| `/api/health` | GET | Check server health |

See [API.md](API.md) for complete API documentation.

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

- **Bundle Size**: ~50KB gzipped (production)
- **Initial Load**: <1s on modern browsers
- **API Polling**: Every 2 seconds (minimal overhead)
- **Memory Usage**: ~10MB typical

## Security Considerations

- **No authentication**: The current implementation has no authentication. If exposing to the internet, add authentication middleware.
- **Input validation**: All inputs are validated client-side, but server-side validation is also performed.
- **CORS**: Enabled for all origins (`*`) in development. Restrict in production.

## Future Enhancements

Planned features:
- [x] Dark mode toggle (implemented!)
- [x] Smart polling that doesn't interfere with editing (implemented!)
- [ ] WebSocket support for real-time updates without polling
- [ ] Enhanced visual color picker component (HTML5 color input)
- [ ] Live preview/thumbnail of display
- [ ] Preset management (save/load favorites)
- [ ] Keyboard shortcuts
- [ ] Carousel mode controls
- [ ] Schedule/timer interface
- [ ] Mobile app (PWA support)
- [ ] Authentication system
- [ ] Multi-user support with change notifications

## Development Tips

### Hot Module Replacement

Vite provides instant HMR. Changes to `App.vue` or `style.css` will update in the browser without a full reload.

### Vue DevTools

Install the Vue DevTools browser extension for debugging:
- Inspect component state
- View reactive data
- Track API calls
- Monitor performance

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

## Related Documentation

- [README.md](../README.md) - Main project documentation
- [API.md](API.md) - API reference
- [SERVER.md](SERVER.md) - Server configuration
- [APPS.md](APPS.md) - Creating custom applications
- [web/README.md](../web/README.md) - Web interface quick start