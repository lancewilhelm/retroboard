# Retroboard Driver

A simple, abstracted driver for controlling RGB LED matrices on Raspberry Pi, with support for both hardware and simulated displays, plus a custom text rendering library and web interface.

## Overview

This driver provides a clean abstraction layer over the `rpi-rgb-led-matrix` library, making it easy to:

- Write code that works with both real hardware and simulated displays
- Test animations and patterns without requiring physical hardware
- Create smooth, tear-free animations using double-buffering
- Render text using BDF bitmap fonts
- Prepare for future web-based emulation of the LED matrix

## Project Structure

```
retroboard/
├── drivers/              # Core driver modules
│   ├── __init__.py       # Package exports
│   ├── matrix.py         # Matrix driver (hardware & simulated)
│   └── text/             # Text rendering library
│       ├── __init__.py
│       └── font.py       # BDF font parser
├── examples/             # Example applications
├── tests/                # Test suite
├── rpi-rgb-led-matrix/   # Underlying C++ library
└── *.py                  # Demo applications (clock, stars, etc.)
```

## Installation

This project uses the `rpi-rgb-led-matrix` library, which should already be installed if you're running on a Raspberry Pi with the hardware.

No additional dependencies are required for the driver wrapper itself.

## Quick Start

### Basic Matrix Control

```python
from drivers import create_driver

# Create a driver (hardware or simulated)
driver = create_driver(use_hardware=True, rows=32, cols=64)

# Set a single pixel to red
driver.set_pixel(0, 0, 255, 0, 0)

# Fill the entire matrix with blue
driver.fill(0, 0, 255)

# Clear the matrix (all pixels to black)
driver.clear()

# Get matrix dimensions
width = driver.get_width()
height = driver.get_height()

# Adjust brightness
driver.set_brightness(50)  # 0-100
```

### Text Rendering

```python
from drivers import create_driver, BDFFont

# Create a driver
driver = create_driver(use_hardware=False, width=64, height=32)

# Load a BDF font
font = BDFFont("./rpi-rgb-led-matrix/fonts/6x10.bdf")

# Create canvas
canvas = driver.create_frame_canvas()

# Draw text (y coordinate is the baseline)
font.draw_text(canvas, x=10, y=20, text="Hello!", r=255, g=255, b=255)

# Update display
canvas = driver.update(canvas)
```

### Double-Buffering for Smooth Animations

```python
from drivers import create_driver

driver = create_driver(use_hardware=True)

# Create an offscreen canvas
canvas = driver.create_frame_canvas()

# Animation loop
while True:
    # Clear the offscreen canvas
    canvas.clear()
    
    # Draw the next frame
    canvas.set_pixel(10, 10, 255, 0, 0)
    
    # Swap buffers atomically (prevents tearing)
    canvas = driver.update(canvas)
```

## Architecture

### Matrix Driver

The driver uses an abstract base class (`MatrixDriver`) that defines a simple interface for controlling LED matrices. Two implementations are provided:

- **HardwareDriver**: Interfaces with real RGB LED matrix hardware via the `rpi-rgb-led-matrix` library
- **SimulatedDriver**: Maintains an in-memory representation of the matrix for testing and future web visualization

### Text Rendering

The custom BDF font parser and renderer:
- Parses BDF (Bitmap Distribution Format) font files
- Works with both hardware and simulated drivers
- Simple, educational Python implementation
- Easy to extend with custom effects

## API Reference

### MatrixDriver Interface

#### Core Drawing (Canvas interface)
```python
driver.set_pixel(x, y, r, g, b)  # Set one pixel
driver.clear()                    # Clear to black
driver.fill(r, g, b)              # Fill with color
driver.get_width()                # Get width
driver.get_height()               # Get height
```

#### Double-Buffering
```python
canvas = driver.create_frame_canvas()       # Create offscreen buffer
canvas = driver.update(canvas)              # Swap buffers, returns old
```

#### Configuration
```python
driver.set_brightness(50)         # Set brightness (0-100)
brightness = driver.get_brightness()  # Get brightness
```

### BDFFont Interface

#### Creating and Loading Fonts
```python
font = BDFFont()                          # Create empty font object
font = BDFFont("path/to/font.bdf")        # Create and load font
font.load_font("path/to/font.bdf")        # Load font from file
```

#### Drawing Text
```python
# Draw text (y is baseline position)
width = font.draw_text(canvas, x, y, text, r, g, b, spacing=0)

# Measure text without drawing
width = font.get_text_width(text, spacing=0)

# Get font height
height = font.height()
```

## Examples

Several example scripts are provided:

- **clock.py**: Digital clock display showing current time in HH:MM:SS format
- **scroll_text.py**: Scrolling text demonstration
- **test_text.py**: Text rendering library tests
- **stars.py**: Maintains a fixed number of "stars" on screen
- **example_driver.py**: Demonstrates basic driver features with various patterns
- **example_double_buffer.py**: Shows double-buffering with smooth animations

Run any example with:
```bash
python3 clock.py                   # Digital clock
python3 scroll_text.py             # Scrolling text
python3 test_text.py               # Text rendering tests
python3 stars.py                   # Pixel queue animation
python3 examples/example_driver.py # Basic features
```

To run examples in simulation mode, edit the script and set `USE_HARDWARE = False`.

## Available Fonts

The `rpi-rgb-led-matrix/fonts/` directory contains many BDF fonts:

- **Tiny**: `4x6.bdf`, `tom-thumb.bdf`
- **Small**: `5x7.bdf`, `5x8.bdf`, `6x9.bdf`
- **Medium**: `6x10.bdf`, `6x12.bdf`, `6x13.bdf`, `7x13.bdf`
- **Large**: `7x14.bdf`, `8x13.bdf`, `9x15.bdf`, `9x18.bdf`
- And many more...

## Testing Without Hardware

You can develop and test your animations without physical hardware:

1. Set `USE_HARDWARE = False` in your script
2. Use `create_driver(use_hardware=False, width=64, height=32)`
3. Call `get_buffer()` on SimulatedDriver to inspect the current state
4. Later, connect to a web visualizer (future feature)

## Documentation

- **README.md** (this file): Overview and API reference
- **QUICKSTART.md**: Quick start guide for new users
- **TEXT_RENDERING.md**: Deep dive into how text rendering works
- **DRIVER_IMPLEMENTATION.md**: Technical implementation details

## How Text Rendering Works

The text library:
1. **Parses BDF files** - Reads bitmap font definitions
2. **Stores glyphs** - Each character is stored as a bitmap
3. **Renders text** - Converts bitmaps to pixels via `set_pixel()`
4. **Works everywhere** - Uses the Canvas interface, so it works with any driver

Unlike the C++ graphics library, this implementation:
- ✅ Works with simulated driver
- ✅ Simple and educational Python code
- ✅ Easy to extend with effects
- ✅ Platform independent

See `TEXT_RENDERING.md` for a detailed explanation of how it works.

## Switching Between Hardware and Simulation

Simply change the `use_hardware` parameter:

```python
# For real hardware
driver = create_driver(use_hardware=True, rows=32, cols=64)

# For simulation (no hardware required)
driver = create_driver(use_hardware=False, width=64, height=32)
```

Then run with sudo for hardware (required for GPIO access):
```bash
sudo python3 your_script.py
```

## Performance Tips

For smooth animations:
1. **Use double-buffering**: Always use `create_frame_canvas()` and `update()` for animations
2. **Minimize allocations**: Reuse the canvas returned by `update()`
3. **Batch operations**: Draw the entire frame before updating
4. **Control frame rate**: Use `time.sleep()` to cap your frame rate

## Contributing

When adding new features:
1. Ensure they work with both HardwareDriver and SimulatedDriver
2. Keep the interface minimal and focused on core operations
3. Add tests and examples
4. Update documentation

## License

This driver wrapper follows the same license as the main retroboard project.

## Matrix Application Server

The retroboard includes an application server that allows you to remotely control the LED matrix through a simple HTTP API or web interface.

### Quick Start

```bash
# Start the server (simulated display)
python3 server.py

# Or with hardware
sudo python3 server.py --hardware
```

The server will start on `http://0.0.0.0:5000` with the clock app running by default.

### Web Interface

A modern Vue 3 web interface is provided for easy control of the LED matrix.

**Installation:**
```bash
cd web
pnpm install
```

**Development:**
```bash
# Terminal 1: Start the RetroBoard server
python3 server.py

# Terminal 2: Start the web interface
cd web
pnpm run dev
```

Then open your browser to `http://localhost:3000`

**Features:**
- 🎮 Switch between apps with a click
- ⚙️ Configure app settings in real-time
- 🎨 Visual color picker for RGB values
- 📊 Live connection status
- 🔴 Stop/start applications

See [web/README.md](web/README.md) for complete web interface documentation.

### Switching Applications via API

```bash
# Switch to scrolling text
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "scroll_text", "config": {"text": "Hello!"}}'

# Switch to stars
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "stars"}'

# Switch to clock
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "clock"}'
```

### Available Applications

- **clock** - Digital clock displaying HH:MM:SS
- **scroll_text** - Scrolling text message
- **stars** - Twinkling colored stars animation

### API Documentation

See [docs/API.md](docs/API.md) for complete API documentation including:
- All available endpoints
- Request/response formats
- Configuration options for each app
- Usage examples

### Testing the API

```bash
# Run the API test suite
python3 test_api.py
```

This will test all endpoints and cycle through the available applications.


## Creating Custom Applications

Apps are automatically discovered - just create a folder in `apps/` with your application class!

### Quick Example

```bash
# 1. Create app folder
mkdir apps/myapp

# 2. Create app.py
cat > apps/myapp/app.py << 'PYTHON'
from apps.base import MatrixApplication
import time

class MyApp(MatrixApplication):
    def setup(self):
        self.canvas = self.driver.create_frame_canvas()
    
    def loop(self):
        # Draw one frame
        self.canvas.clear()
        # ... your drawing code ...
        self.canvas = self.driver.update(self.canvas)
        time.sleep(0.05)
PYTHON

# 3. Restart server - app is automatically discovered!
python3 server.py
```

See [apps/README.md](apps/README.md) for complete guide on creating custom applications.

Each app has its own README:
- [apps/clock/README.md](apps/clock/README.md) - Clock configuration
- [apps/scroll_text/README.md](apps/scroll_text/README.md) - Scrolling text options
- [apps/stars/README.md](apps/stars/README.md) - Stars animation settings

