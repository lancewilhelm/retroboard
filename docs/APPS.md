# Application System Documentation

## Overview

The Matrix Application Server features an automatic app discovery system. Apps are organized in folders with their own README files, making it easy for anyone to create and share applications.

## New Structure

```
apps/
├── base.py              # MatrixApplication base class
├── __init__.py          # Auto-discovery logic
├── README.md            # Guide for creating apps
│
├── clock/               # Clock app
│   ├── __init__.py
│   ├── app.py          # ClockApp implementation
│   └── README.md       # Clock-specific docs
│
├── scroll_text/         # Scrolling text app
│   ├── __init__.py
│   ├── app.py          # ScrollTextApp implementation
│   └── README.md       # Scroll text docs
│
└── stars/               # Stars animation
    ├── __init__.py
    ├── app.py          # StarsApp implementation
    └── README.md       # Stars docs
```

## Key Features

### 1. Auto-Discovery

Apps are automatically discovered at startup:
- Scans all folders in `apps/`
- Imports MatrixApplication subclasses
- Registers using folder name
- **No manual registration needed!**

### 2. Self-Documenting

Each app has its own README with:
- Configuration options
- Usage examples
- How it works explanation

### 3. Easy to Extend

Adding a new app is simple:
1. Create folder: `apps/myapp/`
2. Add app code: `apps/myapp/app.py`
3. Restart server
4. Done!

## How Auto-Discovery Works

```python
# From apps/__init__.py
def discover_apps():
    """Scan apps/ for MatrixApplication subclasses."""
    apps = {}
    for folder in os.listdir('apps/'):
        if is_directory(folder) and not folder.startswith('_'):
            module = import_module(f'apps.{folder}')
            for cls in module:
                if is_subclass(cls, MatrixApplication):
                    apps[folder] = cls
    return apps
```

The system:
1. Scans directories in `apps/`
2. Skips private folders (starting with `_`)
3. Imports each folder as a module
4. Finds MatrixApplication subclasses
5. Maps folder name → app class

## Creating a New App

### Minimal Example

**Create `apps/demo/app.py`:**
```python
from apps.base import MatrixApplication
import time

class DemoApp(MatrixApplication):
    def setup(self):
        self.canvas = self.driver.create_frame_canvas()
        self.x = 0

    def loop(self):
        self.canvas.clear()
        self.canvas.set_pixel(self.x, 10, 255, 0, 0)
        self.canvas = self.driver.update(self.canvas)
        self.x = (self.x + 1) % self.driver.get_width()
        time.sleep(0.05)
```

**Restart server:**
```bash
python3 server.py
# App "demo" is now available!
```

**Use it:**
```bash
curl -X POST http://localhost:5000/api/switch \
  -d '{"app": "demo"}'
```

### With Documentation

**Create `apps/demo/__init__.py`:**
```python
"""Demo application."""
from .app import DemoApp
__all__ = ['DemoApp']
```

**Create `apps/demo/README.md`:**
```markdown
# Demo App

Simple demo application.

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `speed` | number | `1` | Movement speed |
```

## Benefits

### For Developers

- **Easy to Create**: Just implement `setup()` and `loop()`
- **Auto-Registered**: No manual registration code
- **Self-Contained**: Each app in its own folder
- **Well-Documented**: README right next to code

### For Users

- **Easy to Install**: Drop folder in `apps/`, restart
- **Easy to Configure**: Each app has README with options
- **Easy to Remove**: Just delete the folder
- **Easy to Share**: Zip folder, send to friend

### For Maintainers

- **Clean Organization**: One folder per app
- **No Central Registry**: No `__init__.py` to update
- **Extensible**: Anyone can add apps
- **Backward Compatible**: Old imports still work

## Examples

### Clock App

```
apps/clock/
├── __init__.py          # Exports ClockApp
├── app.py               # Implementation
└── README.md            # Config: font, color
```

Usage:
```bash
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "clock", "config": {"color": [255, 0, 0]}}'
```

### Scroll Text App

```
apps/scroll_text/
├── __init__.py          # Exports ScrollTextApp
├── app.py               # Implementation
└── README.md            # Config: text, speed, color, fps
```

Usage:
```bash
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "scroll_text", "config": {"text": "Hello!", "speed": 2}}'
```

## Best Practices

### Folder Naming
- Use lowercase with underscores
- Keep names short and descriptive
- Folder name becomes API name

### File Organization
```
apps/myapp/
├── __init__.py     # Required: exports app class
├── app.py          # Recommended: main code
├── README.md       # Recommended: documentation
└── utils.py        # Optional: helper code
```

### Documentation
- **README.md**: Always include configuration table
- **Examples**: Show common use cases
- **How It Works**: Brief explanation

### Code Style
- Inherit from `MatrixApplication`
- Implement `setup()`, `loop()`, optionally `cleanup()`
- Use `self.config` for configuration
- Override `update_config()` for live updates

## Migration from Old Structure

Old structure (manual registration):
```python
# apps/__init__.py
from .clock import ClockApp
from .scroll_text import ScrollTextApp

# server.py
manager.register_app('clock', ClockApp)
manager.register_app('scroll_text', ScrollTextApp)
```

New structure (auto-discovery):
```python
# server.py
apps = discover_apps()  # Automatic!
for name, cls in apps.items():
    manager.register_app(name, cls)
```

## Future Enhancements

The system is designed to support:
- **App Metadata**: Version, author, description
- **Dependencies**: Declare required packages
- **Thumbnails**: Preview images
- **Categories**: Group related apps
- **App Store**: Browse and install from web

## Summary

✅ **Apps in folders** - Clean organization
✅ **Auto-discovery** - No manual registration
✅ **Self-documenting** - README per app
✅ **Easy to extend** - Drop in folder, restart
✅ **Backward compatible** - Old code still works

The system is lean, simple, and ready for community contributions!
