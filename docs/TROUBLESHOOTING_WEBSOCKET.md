# WebSocket Connection Troubleshooting

Quick guide to fix WebSocket timeout and disconnection issues.

## Common Issue: Connection Problems

### Symptoms

```
WebSocket connection error: Error: timeout
WebSocket connection error: TransportError: websocket error
WebSocket is closed before the connection is established
```

Browser shows "Disconnected" status, connection drops frequently, or fails to connect initially.

## Quick Fix

### 1. Update Vite Configuration

Edit `web/vite.config.js`:

```javascript
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
    plugins: [vue()],
    server: {
        port: 3000,
        proxy: {
            "/api": {
                target: "http://localhost:5000",
                changeOrigin: true,
            },
            "/socket.io": {
                target: "http://localhost:5000",
                changeOrigin: true,
                ws: true,
            },
        },
    },
});
```

### 2. Update Vue App Connection Strategy

Edit `web/src/App.vue` in the `initializeWebSocket()` function:

```javascript
function initializeWebSocket() {
    // Use polling as primary transport for reliability through Vite proxy
    // Socket.IO will upgrade to WebSocket if possible
    socket = io({
        transports: ["polling", "websocket"],
        upgrade: true,
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: Infinity,
        timeout: 20000,
        forceNew: false,
        multiplex: true,
    });
    
    // Log which transport is being used
    socket.on("connect", () => {
        const transport = socket.io.engine.transport.name;
        console.log(`Connected via ${transport}`);
        isConnected.value = true;
    });
    
    // ... rest of the code
}
```

### 4. Restart Everything

```bash
# Stop the server (Ctrl+C)

# Restart backend
cd retroboard
python3 main.py

# In another terminal, restart frontend
cd web
pnpm run dev
```

## Why This Happens

The Vite development server acts as a proxy between the browser and the backend. WebSocket connections through proxies can be unreliable, especially during development.

**The fix:** Use long-polling as the primary transport. It's more reliable through proxies, and Socket.IO will automatically upgrade to WebSocket when the connection is stable.

## Verification

After applying the fix:

1. Open browser to `http://localhost:3000`
2. Open browser console (F12)
3. Look for: `Connected via polling` or `Connected via websocket`
4. Connection indicator should be green
5. Leave the page open for 5+ minutes
6. It should stay connected (polling is stable through proxy)

## Additional Debugging

### Check Server Logs

```bash
# Look for these messages
Client connected via WebSocket
```

If you don't see connection messages, the client isn't reaching the server.

### Check Browser Console

```javascript
// In browser console, check socket status
socket.connected  // Should be true
```

### Monitor Connection Events

Add to your `App.vue`:

```javascript
socket.on('connect', () => {
    const transport = socket.io.engine.transport.name;
    console.log(`✓ Connected via ${transport} at`, new Date().toLocaleTimeString());
});

socket.on('disconnect', (reason) => {
    console.log('✗ Disconnected:', reason, 'at', new Date().toLocaleTimeString());
});

socket.on('reconnect_attempt', (attemptNumber) => {
    console.log(`Reconnecting... attempt ${attemptNumber}`);
});
```

### Check Transport Being Used

In browser console:

```javascript
// Check current transport
socket.io.engine.transport.name  // Returns "polling" or "websocket"

// Listen for transport changes
socket.io.engine.on('upgrade', (transport) => {
    console.log('Upgraded to:', transport.name);
});
```

**Note:** Polling is perfectly fine! It works reliably through the Vite proxy and still provides real-time updates.

## Production Deployment

For production, ensure your reverse proxy (nginx/Apache) is configured for WebSocket:

### nginx

```nginx
location / {
    proxy_pass http://localhost:5000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;  # 24 hours
}
```

### Apache

```apache
ProxyPass / http://localhost:5000/
RewriteEngine On
RewriteCond %{HTTP:Upgrade} websocket [NC]
RewriteRule /(.*) ws://localhost:5000/$1 [P,L]
ProxyTimeout 86400
```

## Still Not Working?

1. **Check firewall:** Ensure port 5000 is accessible
2. **Check CORS:** May need specific origins instead of "*"
3. **Try different browser:** Rule out browser-specific issues
4. **Disable browser extensions:** Some extensions interfere with WebSocket
5. **Check network:** Corporate networks may block WebSocket

## Summary

The most common issue is WebSocket connections being unreliable through the Vite dev server proxy. The solution is to use long-polling as the primary transport, which is stable through proxies.

**Key settings:**
- Transport order: `["polling", "websocket"]` - polling first for reliability
- Auto-upgrade: Socket.IO will upgrade to WebSocket when stable
- Infinite reconnect: Never stops trying to reconnect
- Works through proxy: Long-polling is proxy-friendly

**Remember:** Polling provides the same real-time experience - updates still arrive instantly!