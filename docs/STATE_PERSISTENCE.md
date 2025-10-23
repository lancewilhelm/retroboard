# State Persistence

The RetroBoard server automatically saves and restores the state of applications, allowing seamless recovery after restarts.

## Overview

State persistence tracks:
1. **Last Running App**: Which app was active when the server stopped
2. **App Configurations**: The last known configuration for each app

This ensures that when you restart the server, everything returns to exactly how you left it.

## How It Works

### State File

State is saved to `state.json` in the project root directory:

```json
{
  "last_app": "scroll_text",
  "app_configs": {
    "clock": {
      "font": "tom-thumb",
      "color": [255, 0, 0]
    },
    "scroll_text": {
      "text": "Welcome back!",
      "font": "6x10",
      "color": [0, 255, 0],
      "speed": 2,
      "fps": 30
    },
    "stars": {
      "spawn_rate": 3,
      "lifetime": 50,
      "fps": 60
    }
  }
}
```

### When State is Saved

State is automatically saved:
- ✅ After switching to a different app
- ✅ After updating an app's configuration
- ✅ When user explicitly stops an app (clears `last_app`)
- ✅ On server shutdown via Ctrl+C (preserves `last_app` for restart)

### When State is Loaded

State is loaded once during server startup:
- ✅ On `python3 main.py` startup
- ✅ Before registering apps
- ✅ Before starting the initial app

## Startup Behavior

### With Saved State

```bash
$ python3 main.py
# Loads state.json
# Restores last running app with its saved configuration
```

**Priority Order:**
1. **Saved state** (if exists and valid)
2. Command line `--app` argument
3. First available app (fallback)

### Without Saved State

First run or after deleting `state.json`:
- Uses command line `--app` argument (default: `clock`)
- Starts with default configuration
- Creates `state.json` on first config change

### Ignoring Saved State

Force a fresh start:
```bash
python3 main.py --ignore-state
```

This will:
- Skip loading `state.json`
- Start with command line arguments or defaults
- Still save state going forward

### Stopping the Server

When you stop the server with **Ctrl+C**:
- Current app config is saved
- `last_app` is **preserved** (so it restarts on next boot)
- Clean shutdown of current app

When you **stop an app via API** (`POST /api/stop`):
- Current app config is saved
- `last_app` is set to `null` (no app will auto-start)
- Display goes blank

## Examples

### Example 1: Normal Usage

```bash
# First run
$ python3 main.py
# Starts with clock (default)

# Use web interface to:
# - Switch to scroll_text
# - Set text to "Hello World"
# - Change color to red

# Stop server (Ctrl+C)
# Note: last_app is preserved!

# Restart server
$ python3 main.py
# Automatically starts scroll_text with "Hello World" in red!
```

### Example 1b: Stop App vs Server

```bash
# Start server
$ python3 main.py

# Via API or web UI: Stop the app
curl -X POST http://localhost:5000/api/stop

# Restart server
$ python3 main.py
# No app starts automatically (last_app was cleared)

# But if you switch to an app and use Ctrl+C...
curl -X POST http://localhost:5000/api/switch -d '{"app":"clock"}'
# (Ctrl+C to stop server)

# Restart server
$ python3 main.py
# Clock starts automatically! (last_app was preserved)
```

### Example 2: Per-App Memory

```bash
# Start server
$ python3 main.py

# Via web UI:
# - Configure clock with red color
# - Switch to stars with spawn_rate=5
# - Switch to scroll_text with custom message
# - Switch back to clock

# Clock still has red color (remembered!)

# Restart server
$ python3 main.py
# Scroll_text starts (it was last running)

# Switch to clock via UI
# Clock still has red color (persisted!)
```

### Example 3: Command Line Override

```bash
# You have scroll_text saved as last app
$ python3 main.py --app stars
# Starts with stars instead (overrides saved state)
# Stars still uses its saved configuration
```

### Example 4: Fresh Start

```bash
# Reset everything
$ python3 main.py --ignore-state --app clock
# Starts fresh with default clock settings
# Still saves state going forward
```

## File Management

### Location

- File: `state.json`
- Path: Project root directory (`retroboard/state.json`)
- Format: Human-readable JSON

### Version Control

The state file is automatically excluded from git:
```gitignore
state.json
```

This is appropriate because:
- State is user-specific
- Different per deployment
- Not part of the codebase

### Manual Editing

You can manually edit `state.json`:

```bash
# Open in editor
nano state.json

# Modify values
{
  "last_app": "clock",
  "app_configs": {
    "clock": {
      "color": [255, 255, 255]
    }
  }
}

# Restart server to apply changes
python3 main.py
```

### Backup

To backup your state:
```bash
cp state.json state.backup.json
```

To restore:
```bash
cp state.backup.json state.json
python3 main.py
```

### Reset

To reset all state:
```bash
rm state.json
python3 main.py
```

## Error Handling

### Missing State File

**What happens:**
- First run or after deletion
- Logs: "No state file found, using defaults"
- Uses command line arguments or defaults

**Action:** None needed, this is normal

### Corrupted State File

**What happens:**
- JSON parse error
- Logs: "Failed to parse state file"
- Falls back to defaults
- File will be overwritten on next save

**Action:** Delete or fix the file manually

### Saved App Doesn't Exist

**What happens:**
- App was deleted or renamed
- Logs: Warning about missing app
- Falls back to command line argument or first available app
- Invalid app removed from state on next save

**Action:** None needed, handled automatically

### Invalid Configuration

**What happens:**
- Saved config has invalid values
- App's `setup()` method validates values
- Invalid values replaced with defaults

**Action:** Check app implementation if issues persist

## API Behavior

The web interface automatically reflects saved state:

1. **On page load:**
   - UI fetches current app and config
   - Displays whatever is running (which may be restored from state)

2. **After restart:**
   - UI sees the restored app
   - Configuration shows saved values
   - No manual refresh needed

3. **After config changes:**
   - Changes are saved immediately
   - Persisted across restarts
   - UI stays in sync via polling

## Under the Hood

### ApplicationManager Integration

The `ApplicationManager` class handles all state persistence:

```python
# Save state
manager.save_state()
# Saves: last_app + all app_configs

# Load state
last_app, configs = manager.load_state()
# Returns: (app_name, config_dict)

# Get saved config for an app
config = manager.get_app_config('clock')
```

### Automatic Triggers

State is saved automatically via these `ApplicationManager` methods:
- `switch_app()` - After successful switch
- `stop_current_app()` - After stopping
- `process_commands()` - After config update

### State Structure

```python
{
    'last_app': str or None,
    'app_configs': {
        'app_name': {
            'key': value,
            ...
        },
        ...
    }
}
```

## Best Practices

### For Users

1. **Let it work automatically** - No manual intervention needed
2. **Use `--ignore-state` sparingly** - Only when you want a fresh start
3. **Check logs** - If state doesn't restore, check startup logs
4. **Backup important configs** - Copy `state.json` if you have perfect settings

### For Developers

1. **App configs must be JSON-serializable** - No functions, objects, etc.
2. **Provide sensible defaults** - Apps should work without saved state
3. **Validate configurations** - Don't assume saved values are valid
4. **Use `get_config()`** - Always return current config from this method

### For System Administrators

1. **Include state.json in backups** - If you want to preserve settings
2. **Exclude from git** - Already in `.gitignore`
3. **Monitor file size** - Should stay small (<100KB typically)
4. **Permissions** - Ensure write access to project directory

## Troubleshooting

### State Not Restoring

**Check:**
1. Does `state.json` exist in project root?
2. Is the file readable? (check permissions)
3. Is the JSON valid? (check with `cat state.json`)
4. Check logs for error messages

**Solution:**
```bash
# Verify file exists
ls -la state.json

# Check contents
cat state.json

# Validate JSON
python3 -c "import json; json.load(open('state.json'))"

# Check logs
python3 main.py 2>&1 | grep -i state
```

### Different State Than Expected

**Possible causes:**
1. State was overwritten by another instance
2. Config change didn't save (check logs)
3. App validation changed config values

**Solution:**
- Check server logs for save/load messages
- Verify `state.json` contents
- Try `--ignore-state` for fresh start

### Can't Save State

**Possible causes:**
1. No write permission to project directory
2. Disk full
3. File system error

**Solution:**
```bash
# Check permissions
ls -ld .
# Should have write permission

# Check disk space
df -h .

# Try manual write
echo '{}' > state.json
```

## Migration Notes

### Upgrading from Pre-Persistence Version

State persistence is backwards compatible:
- Old installations: No state file → uses defaults
- First config change → state file created
- Future runs → state restored

No migration needed!

### Future Version Changes

If state format changes in future versions:
- Old state files will be handled gracefully
- Incompatible fields ignored
- Valid fields preserved
- Logs will indicate version mismatch

## Related Documentation

- [SERVER.md](SERVER.md) - Server architecture
- [API.md](API.md) - API endpoints
- [APPS.md](APPS.md) - Creating applications
- [WEB_INTERFACE.md](WEB_INTERFACE.md) - Web UI usage