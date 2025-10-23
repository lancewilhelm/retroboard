# Web Interface Testing Guide

This guide helps you test the RetroBoard web interface to ensure everything is working correctly.

## Prerequisites

Before testing, ensure you have:
- RetroBoard server installed and configured
- Python virtual environment with Flask and flask-cors
- Node.js 16+ and pnpm installed
- Web dependencies installed (`cd web && pnpm install`)

## Quick Test Checklist

### ✅ Setup Verification

```bash
# 1. Check Python dependencies
~/venvs/matrix/bin/pip list | grep -E "flask|cors"
# Should show: flask and flask-cors

# 2. Check web dependencies
cd web
pnpm list vue vite
# Should show: vue@3.4.0 and vite@5.0.0

# 3. Verify server can start
cd ..
python3 server.py &
SERVER_PID=$!
sleep 2
curl http://localhost:5000/api/health
kill $SERVER_PID
# Should return: {"status": "ok", ...}
```

### ✅ Development Server Test

**Terminal 1 - Start RetroBoard Server:**
```bash
cd ~/retroboard
python3 server.py
```

Expected output:
```
Starting Matrix Application Server
Driver: SimulatedDriver (64x32)
Starting app: clock
API Server: http://0.0.0.0:5000
```

**Terminal 2 - Start Web Dev Server:**
```bash
cd ~/retroboard/web
pnpm run dev
```

Expected output:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

**Browser Test:**
1. Open http://localhost:3000
2. You should see:
   - Purple gradient background
   - "RetroBoard Controller" header
   - Green "Connected" status indicator
   - Current app showing "clock"
   - Three app cards: Clock, Scroll Text, Stars

### ✅ Functional Tests

#### Test 1: Connection Status
- **Expected**: Green dot with "Connected" in header
- **If Red**: Check that server.py is running on port 5000

#### Test 2: App Switching
1. Click on "Scroll Text" card
2. Card should highlight with blue border
3. Configuration form should appear below
4. Enter text: "Testing 123"
5. Click "Switch to App"
6. "Current App" should change to "Scroll Text"

#### Test 3: Configuration Updates
1. With Scroll Text running, change speed to 5
2. Click "Update Config"
3. Text on display should scroll faster

#### Test 4: Color Picker
1. Select Clock app
2. Change RGB values: R=255, G=0, B=0
3. Color preview square should turn red
4. Click "Switch to App"
5. Clock should display in red

#### Test 5: Stop App
1. Click "Stop App" button
2. Current App should show "None"
3. Display should be blank

### ✅ API Integration Tests

Run these curl commands while the web interface is open:

```bash
# Test 1: List apps
curl http://localhost:5000/api/apps
# Should return: {"apps": ["clock", "scroll_text", "stars"], "current": "..."}

# Test 2: Get current app
curl http://localhost:5000/api/current
# Should return: {"app": "...", "config": {...}}

# Test 3: Switch app via API (should update web UI)
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "stars"}'
# Web UI should update to show "stars" as current app

# Test 4: Update config via API (should update web UI)
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"spawn_rate": 5}'
# Web UI should reflect new config after next poll (2 seconds)
```

### ✅ Browser Compatibility Tests

Test in these browsers:
- [ ] Chrome/Edge 90+
- [ ] Firefox 88+
- [ ] Safari 14+

Verify:
- Layout renders correctly
- All buttons work
- Color preview displays
- No console errors

### ✅ Responsive Design Tests

Test at these viewport sizes:
- [ ] Desktop: 1920x1080
- [ ] Laptop: 1366x768
- [ ] Tablet: 768x1024
- [ ] Mobile: 375x667

Verify:
- App cards wrap appropriately
- Forms remain usable
- No horizontal scrolling
- All text readable

## Common Issues and Solutions

### Issue: "Cannot connect to server"

**Symptoms**: Red status dot, no apps listed

**Solutions**:
```bash
# Check if server is running
curl http://localhost:5000/api/health

# Check server logs for errors
# Look at Terminal 1 output

# Verify port is not in use
lsof -i :5000

# Restart both servers
# Ctrl+C in both terminals, then restart
```

### Issue: "CORS errors in console"

**Symptoms**: API requests fail, CORS errors in browser console

**Solutions**:
```bash
# Verify flask-cors is installed
~/venvs/matrix/bin/pip list | grep flask-cors

# Install if missing
~/venvs/matrix/bin/pip install flask-cors

# Restart server
```

### Issue: "Vite proxy not working"

**Symptoms**: 404 errors for /api/* requests

**Solutions**:
```bash
# Check vite.config.js exists and has proxy config
cat web/vite.config.js | grep -A5 proxy

# Restart Vite dev server
# Ctrl+C and run: pnpm run dev
```

### Issue: "Changes not appearing"

**Symptoms**: Configuration changes don't affect display

**Solutions**:
1. Ensure you clicked "Switch to App" or "Update Config"
2. Check server logs for error messages
3. Verify values are within valid ranges (RGB: 0-255, etc.)
4. Try switching to a different app and back

### Issue: "Build fails"

**Symptoms**: `pnpm run build` errors

**Solutions**:
```bash
# Clean install
cd web
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Check Node version
node --version
# Should be 16+

# Try building again
pnpm run build
```

## Performance Tests

### Test 1: Bundle Size
```bash
cd web
pnpm run build
du -sh dist/
# Should be < 200KB
```

### Test 2: Load Time
1. Open browser DevTools (F12)
2. Go to Network tab
3. Load http://localhost:3000
4. Check total load time
   - Expected: < 1 second on local network

### Test 3: Memory Usage
1. Open browser DevTools
2. Go to Memory tab
3. Take heap snapshot
4. Check size
   - Expected: < 15MB

### Test 4: API Polling
1. Open browser DevTools
2. Go to Network tab
3. Watch for /api/current requests
4. Verify they occur every ~2 seconds
5. Check response time
   - Expected: < 50ms

## Automated Testing

Currently, the web interface doesn't have automated tests. To add them:

```bash
# Install Vitest (future enhancement)
pnpm add -D vitest @vue/test-utils jsdom

# Run tests
pnpm test
```

## Manual Test Script

Run through this script for complete verification:

```bash
# 1. Start servers
python3 server.py &
cd web && pnpm run dev &

# Wait for startup
sleep 5

# 2. Test API endpoints
echo "Testing /api/health..."
curl -s http://localhost:5000/api/health | jq

echo "Testing /api/apps..."
curl -s http://localhost:5000/api/apps | jq

echo "Testing /api/current..."
curl -s http://localhost:5000/api/current | jq

# 3. Test app switching
echo "Switching to stars..."
curl -s -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "stars"}' | jq

sleep 2

echo "Switching to scroll_text..."
curl -s -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "scroll_text", "config": {"text": "Test Message"}}' | jq

# 4. Open browser
echo "Opening browser..."
open http://localhost:3000  # macOS
# xdg-open http://localhost:3000  # Linux

# 5. Manual checks in browser:
echo ""
echo "Manual checks:"
echo "1. Verify 'Connected' status is green"
echo "2. Click each app card and verify config forms appear"
echo "3. Change settings and click 'Switch to App'"
echo "4. Verify display updates (check Terminal 1)"
echo "5. Test 'Stop App' button"
echo ""
echo "Press Enter when done testing..."
read

# 6. Cleanup
killall python3 2>/dev/null
killall node 2>/dev/null
echo "Test complete!"
```

## Network Access Testing

To test from other devices on your network:

```bash
# 1. Find your IP address
ifconfig | grep "inet " | grep -v 127.0.0.1

# 2. Start server with network access
python3 server.py --host 0.0.0.0

# 3. Update vite.config.js proxy target to your IP
# Edit web/vite.config.js:
#   target: 'http://192.168.1.X:5000'

# 4. Start dev server with network access
cd web
pnpm run dev -- --host

# 5. Access from another device
# http://192.168.1.X:3000
```

## Production Build Testing

```bash
# 1. Build for production
cd web
pnpm run build

# 2. Preview production build
pnpm run preview

# 3. Test production build
open http://localhost:4173

# 4. Verify:
# - All features work
# - No console errors
# - Fast load time
# - Small bundle size
```

## Reporting Issues

When reporting issues, include:
1. Browser and version
2. Node.js version (`node --version`)
3. pnpm version (`pnpm --version`)
4. Error messages from browser console
5. Server logs from Terminal 1
6. Steps to reproduce

## Success Criteria

The web interface is working correctly when:
- ✅ Status shows "Connected"
- ✅ All three apps appear in app grid
- ✅ Current app displays correctly
- ✅ Configuration forms appear when apps are selected
- ✅ Switching apps works (display changes)
- ✅ Configuration updates work (display changes)
- ✅ Color preview displays correct colors
- ✅ Stop button clears display
- ✅ No errors in browser console
- ✅ No errors in server logs

## Next Steps

After successful testing:
1. Use the web interface to control your RetroBoard
2. Create custom apps (see `apps/README.md`)
3. Share your configurations
4. Build for production if deploying (`pnpm run build`)

For more information, see:
- `web/README.md` - Quick start guide
- `docs/WEB_INTERFACE.md` - Complete documentation
- `docs/API.md` - API reference