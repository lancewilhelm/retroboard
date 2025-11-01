# WebSocket Migration Guide

This guide explains the migration from HTTP polling to WebSocket-based real-time communication in RetroBoard.

## What Changed?

### Before (Polling)
- Web interface polled `/api/current` every 2 seconds
- High server load with many clients
- 2-second delay for updates
- Unnecessary bandwidth usage

### After (WebSocket)
- Persistent WebSocket connection
- Real-time updates (instant)
- Server pushes changes only when needed
- Lower server load and bandwidth usage

## For End Users

### Installation

Update your Python dependencies:

```bash
cd retroboard
pip install -r requirements.txt
```

This installs:
- `flask-socketio>=5.3.0`
- `python-socketio>=5.9.0`

Update web dependencies:

```bash
cd web
pnpm install
```

This installs:
- `socket.io-client@^4.7.0`

### Usage

**No changes required!** The web interface automatically uses WebSocket when you open it.

You'll notice:
- Faster updates (no 2-second delay)
- The connection indicator responds immediately
- App changes appear instantly

### Troubleshooting

#### WebSocket Connection Fails

If you see "Disconnected" in the web interface:

1. **Check server is running:**
   ```bash
   curl http://localhost:5000/api/health
   ```

2. **Check logs for WebSocket errors:**
   ```bash
   # Look for "Client connected via WebSocket" messages
   ```

3. **Verify firewall allows WebSocket:**
   - WebSocket uses same port as HTTP (default: 5000)
   - Ensure port is open for both HTTP and WebSocket traffic

4. **Try fallback to polling:**
   - If WebSocket fails, Socket.IO automatically falls back to polling
   - Check browser console for connection details

#### Server Won't Start

```
ModuleNotFoundError: No module named 'flask_socketio'
```

**Solution:**
```bash
pip install flask-socketio python-socketio
```

#### Port Already in Use

```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find and kill the process using port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port
python3 main.py --port 5001
```

## For Developers

### API Compatibility

All REST endpoints remain unchanged. WebSocket is additive, not breaking.

**REST API**: Still works exactly as before
```bash
curl -X POST http://localhost:5000/api/switch \
  -d '{"app": "clock"}'
```

**WebSocket**: New real-time updates
```javascript
socket.on('current_app', (data) => {
  console.log('App changed:', data.app);
});
```

### Migrating Custom Clients

If you have custom clients that poll the API, consider migrating to WebSocket:

#### Before (Polling)
```python
import requests
import time

while True:
    response = requests.get('http://localhost:5000/api/current')
    data = response.json()
    print(f"Current app: {data['app']}")
    time.sleep(2)  # Poll every 2 seconds
```

#### After (WebSocket)
```python
import socketio

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected!')
    sio.emit('request_state')

@sio.on('current_app')
def on_current_app(data):
    print(f"Current app: {data['app']}")

sio.connect('http://localhost:5000')
sio.wait()
```

**Benefits:**
- Instant updates (no 2-second delay)
- Lower CPU usage (no polling loop)
- Better for battery (on mobile/laptop)
- Scales better with multiple clients

### WebSocket Events Reference

#### Client to Server

| Event | Purpose | Example |
|-------|---------|---------|
| `connect` | Auto-emitted on connection | N/A |
| `disconnect` | Auto-emitted on disconnection | N/A |
| `request_state` | Request complete state | `socket.emit('request_state')` |

#### Server to Client

| Event | When Emitted | Data |
|-------|--------------|------|
| `apps_list` | App list changes, on connect | `{apps: [...], current: "clock"}` |
| `current_app` | App switches, config updates | `{app: "clock", config: {...}}` |
| `settings` | Brightness changes | `{brightness: 75}` |
| `carousel_config` | Carousel enabled/disabled/updated | `{enabled: true, apps: [...]}` |

### Backward Compatibility

The REST API is fully preserved:

```bash
# These still work exactly as before
GET  /api/apps
GET  /api/current
POST /api/switch
POST /api/config
GET  /api/carousel
POST /api/carousel
GET  /api/settings
POST /api/settings
```

**Best Practice**: Use REST for commands, WebSocket for updates
```javascript
// Send command via REST
await fetch('/api/switch', {
  method: 'POST',
  body: JSON.stringify({app: 'clock'})
});

// Receive confirmation via WebSocket
socket.on('current_app', (data) => {
  // Update UI immediately
});
```

## Architecture Changes

### Server Side

**main.py:**
```python
# Before
api_app = create_api(manager)
api_app.run(host=args.host, port=args.port)

# After
api_app, socketio = create_api(manager)
socketio.run(api_app, host=args.host, port=args.port)
```

**api.py:**
```python
# Added
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    # Send initial state to client
    pass
```

**manager.py:**
```python
# Added
def _emit_current_app(self):
    """Emit state change via WebSocket."""
    if self.socketio:
        self.socketio.emit('current_app', {...})
```

### Client Side

**App.vue:**
```javascript
// Before
let pollInterval = setInterval(async () => {
  await fetchCurrentApp();
}, 2000);

// After
import { io } from 'socket.io-client';

const socket = io();

socket.on('current_app', (data) => {
  currentApp.value = data.app;
});
```

## Performance Impact

### Server Load

With 10 concurrent clients:

**Before (Polling):**
- 10 clients × 0.5 requests/sec = 5 requests/sec
- 5 requests × 24 hours = 432,000 requests/day
- Constant CPU usage from polling

**After (WebSocket):**
- 10 persistent connections
- Updates only on state change (~10-100/day)
- Near-zero idle CPU usage

### Network Traffic

**Before:**
- Each poll: ~500 bytes (request + response)
- 10 clients × 0.5 req/sec × 500 bytes = 2.5 KB/sec
- Per day: ~216 MB

**After:**
- Connection: ~1 KB (initial handshake)
- Updates: ~200 bytes each
- Per day with 50 updates: ~10 KB

**Savings: 99.95% reduction in bandwidth**

## Testing

### Verify WebSocket Works

1. **Start the server:**
   ```bash
   python3 main.py
   ```

2. **Check startup logs:**
   ```
   WebSocket available at: ws://0.0.0.0:5000
   ```

3. **Open web interface:**
   ```bash
   cd web
   pnpm run dev
   ```

4. **Check browser console:**
   ```
   WebSocket connected
   ```

5. **Test real-time updates:**
   ```bash
   # In another terminal
   curl -X POST http://localhost:5000/api/switch \
     -H "Content-Type: application/json" \
     -d '{"app": "stars"}'
   ```

   The web interface should update **instantly** (no 2-second delay).

### Manual WebSocket Test

Use a WebSocket client to test directly:

```javascript
// In browser console
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected!');
  socket.emit('request_state');
});

socket.on('current_app', (data) => {
  console.log('Current app:', data);
});
```

## Rollback (If Needed)

If you need to rollback to polling (not recommended):

### 1. Server Side
No changes needed - REST API still works.

### 2. Client Side

In `web/src/App.vue`, replace WebSocket code with polling:

```javascript
// Remove WebSocket initialization
// initializeWebSocket();

// Add back polling
let pollInterval = setInterval(async () => {
  await fetchCurrentAppOnly();
}, 2000);

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval);
  }
});
```

### 3. Remove Dependencies

```bash
# Python
pip uninstall flask-socketio python-socketio

# JavaScript
cd web
pnpm remove socket.io-client
```

**Note:** Rollback is not recommended. WebSocket provides significant benefits with no downsides.

## Common Issues

### Issue: High CPU Usage

**Symptom:** Server using more CPU than before

**Cause:** `async_mode` not set correctly

**Solution:**
```python
# In api.py
socketio = SocketIO(app, 
                    cors_allowed_origins="*", 
                    async_mode="threading")  # Important!
```

### Issue: WebSocket Disconnects Frequently

**Symptom:** Connection drops every few minutes

**Possible Causes:**
1. Reverse proxy timeout (nginx, Apache)
2. Firewall closing idle connections
3. Network instability

**Solutions:**

**For nginx:**
```nginx
location / {
    proxy_pass http://localhost:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;  # 24 hours
}
```

**For Apache:**
```apache
ProxyPass / http://localhost:5000/
ProxyPassReverse / http://localhost:5000/
RewriteEngine On
RewriteCond %{HTTP:Upgrade} websocket [NC]
RewriteRule /(.*) ws://localhost:5000/$1 [P,L]
ProxyTimeout 86400
```

### Issue: CORS Errors

**Symptom:** WebSocket connection blocked by CORS

**Solution:**
```python
# In api.py
socketio = SocketIO(app, 
                    cors_allowed_origins="*",  # Or specific origin
                    async_mode="threading")
```

For production, restrict origins:
```python
cors_allowed_origins=["https://yourdomain.com"]
```

## Deployment Considerations

### Production Deployment

1. **Use a proper ASGI server:**
   ```bash
   pip install eventlet
   ```
   
   ```python
   # In main.py
   socketio.run(api_app, 
                host=args.host, 
                port=args.port,
                debug=False)
   ```

2. **Configure reverse proxy for WebSocket:**
   - Ensure WebSocket upgrade headers are passed
   - Set appropriate timeouts
   - Enable keep-alive

3. **Monitor connections:**
   ```python
   # Add logging
   @socketio.on('connect')
   def handle_connect():
       logger.info(f"Client connected: {request.sid}")
   ```

### Scaling

WebSocket connections are stateful. For multiple server instances:

1. **Use Redis for message passing:**
   ```python
   socketio = SocketIO(app, 
                       message_queue='redis://localhost:6379')
   ```

2. **Sticky sessions in load balancer:**
   - Ensure client stays on same server
   - Or use Redis adapter (recommended)

## Support

If you encounter issues after migration:

1. Check server logs for errors
2. Check browser console for WebSocket errors
3. Verify firewall/proxy allows WebSocket
4. Test REST API still works: `curl http://localhost:5000/api/health`
5. Open an issue on GitHub with logs

## Summary

✅ **Benefits:**
- Instant real-time updates
- 99%+ reduction in bandwidth
- Lower server CPU usage
- Better scalability
- Improved user experience

✅ **No Breaking Changes:**
- REST API fully preserved
- Existing scripts still work
- Graceful fallback to polling

✅ **Simple Migration:**
- `pip install -r requirements.txt`
- `pnpm install`
- Restart server

The WebSocket upgrade is a significant improvement with no downsides. All existing functionality is preserved while adding real-time capabilities.