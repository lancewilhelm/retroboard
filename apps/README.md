# Matrix Applications

This directory contains all available applications for the LED matrix. Apps are automatically discovered and registered - just drop in a new folder!

## Available Apps

- **[clock](clock/)** - Digital clock display
- **[scroll_text](scroll_text/)** - Scrolling text message
- **[stars](stars/)** - Twinkling stars animation

Each app has its own README with configuration details.

## Creating a New App

### Quick Start

1. Create a new folder in `apps/` with your app name
2. Create an `app.py` file with your MatrixApplication subclass
3. Optionally create `__init__.py` and `README.md`
4. Your app is automatically discovered!

### Example: Creating a "Rainbow" App

**Step 1: Create the folder**
```bash
mkdir apps/rainbow
```

**Step 2: Create `apps/rainbow/app.py`**
```python
"""Rainbow gradient animation."""
import time
from apps.base import MatrixApplication

class RainbowApp(MatrixApplication):
    """Displays a moving rainbow gradient."""
    
    def setup(self):
        """Initialize the rainbow app."""
        self.hue_offset = 0
        self.speed = self.config.get('speed', 1)
        self.canvas = self.driver.create_frame_canvas()
        self.width = self.driver.get_width()
        self.height = self.driver.get_height()
    
    def loop(self):
        """Draw one frame of the rainbow."""
        self.canvas.clear()
        
        # Draw rainbow gradient
        for x in range(self.width):
            hue = (self.hue_offset + x * 5) % 360
            r, g, b = self.hsv_to_rgb(hue)
            
            for y in range(self.height):
                self.canvas.set_pixel(x, y, r, g, b)
        
        self.canvas = self.driver.update(self.canvas)
        self.hue_offset = (self.hue_offset + self.speed) % 360
        time.sleep(0.03)
    
    def hsv_to_rgb(self, h):
        """Convert HSV to RGB (simplified)."""
        # Convert hue (0-360) to RGB
        # (Simple implementation - you'd want a better one)
        h = h / 60.0
        i = int(h)
        f = h - i
        
        if i == 0: return (255, int(255 * f), 0)
        if i == 1: return (int(255 * (1-f)), 255, 0)
        if i == 2: return (0, 255, int(255 * f))
        if i == 3: return (0, int(255 * (1-f)), 255)
        if i == 4: return (int(255 * f), 0, 255)
        return (255, 0, int(255 * (1-f)))
```

**Step 3: Create `apps/rainbow/__init__.py`** (optional but recommended)
```python
"""Rainbow gradient animation."""
from .app import RainbowApp

__all__ = ['RainbowApp']
```

**Step 4: Create `apps/rainbow/README.md`** (optional but helpful)
```markdown
# Rainbow App

Animated rainbow gradient that scrolls horizontally.

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `speed` | number | `1` | Animation speed |

## Example

curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "rainbow", "config": {"speed": 3}}'
```

**Step 5: Restart server**
```bash
python3 server.py
```

Your app is now available! The server will automatically discover and register it.

## App Structure

### Minimal App

```python
from apps.base import MatrixApplication
import time

class MinimalApp(MatrixApplication):
    def setup(self):
        # Initialize once - load fonts, create canvas, etc.
        self.canvas = self.driver.create_frame_canvas()
        self.x = 0
    
    def loop(self):
        # Draw ONE frame
        self.canvas.clear()
        self.canvas.set_pixel(self.x, 10, 255, 0, 0)
        self.canvas = self.driver.update(self.canvas)
        
        self.x = (self.x + 1) % self.driver.get_width()
        time.sleep(0.05)
    
    # cleanup() is optional - base class clears display
```

### With Configuration

```python
class ConfigurableApp(MatrixApplication):
    def setup(self):
        # Read config values
        self.color = self.config.get('color', [255, 0, 0])
        self.speed = self.config.get('speed', 1)
        # ... rest of setup
    
    def update_config(self, key, value):
        # Handle live config updates
        super().update_config(key, value)
        
        if key == 'color':
            self.color = value
        elif key == 'speed':
            self.speed = value
```

## Naming Conventions

- **Folder name** = app name in API (e.g., `rainbow` → `"app": "rainbow"`)
- **Class name** = PascalCase with "App" suffix (e.g., `RainbowApp`)
- **File name** = `app.py` (recommended for consistency)

## Auto-Discovery

The system automatically:
1. Scans all folders in `apps/`
2. Skips folders starting with `_`
3. Imports each folder as a module
4. Looks for classes that inherit from `MatrixApplication`
5. Registers them using the folder name

**No manual registration needed!** Just create the folder and restart the server.

## Best Practices

### 1. Keep loop() Fast
```python
def loop(self):
    # Good: One frame, quick return
    self.draw_frame()
    time.sleep(0.03)
    
    # Bad: Long blocking operation
    for i in range(1000):
        self.do_something()  # Takes forever!
```

### 2. Check should_stop() for Long Operations
```python
def loop(self):
    for i in range(100):
        if self.should_stop():
            break
        self.process_item(i)
```

### 3. Use Instance Variables for State
```python
def setup(self):
    self.counter = 0
    self.items = []

def loop(self):
    self.counter += 1
    # Use self.counter, self.items
```

### 4. Clean Up Resources
```python
def cleanup(self):
    # If you have special cleanup needs
    self.save_state()
    super().cleanup()  # Calls base cleanup (clears display)
```

### 5. Handle Config Changes
```python
def update_config(self, key, value):
    super().update_config(key, value)
    
    if key == 'text':
        self.text = value
        self.recalculate_width()
```

## Debugging

Add logging to your app:
```python
import logging

logger = logging.getLogger(__name__)

class MyApp(MatrixApplication):
    def setup(self):
        logger.info("MyApp starting...")
        # ...
    
    def loop(self):
        logger.debug(f"Drawing frame {self.frame_count}")
        # ...
```

## Testing

Test your app before deploying:
```python
from drivers import create_driver
from apps.myapp import MyApp

driver = create_driver(use_hardware=False, width=32, height=32)
app = MyApp(driver, {'speed': 5})
app.setup()

# Run a few iterations
for _ in range(10):
    app.loop()

app.cleanup()
print("✅ App works!")
```

## Sharing Apps

To share your app:
1. Zip the app folder
2. Include the README.md
3. Users just unzip into their `apps/` directory
4. Restart server - done!

## Examples

Look at the existing apps for examples:
- **clock** - Simple app with time display
- **scroll_text** - Animated scrolling with config
- **stars** - Complex state management with particles

## Tips

- Start simple, add complexity gradually
- Test in simulated mode first
- Use small fonts for 32x64 displays
- Keep FPS reasonable (30-60 is usually enough)
- Add config options for customization
- Document your config in README

Happy coding! 🎨
