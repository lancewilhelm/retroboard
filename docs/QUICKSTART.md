# Driver Wrapper Quick Start Guide

Get started with the Retroboard driver wrapper in 5 minutes!

## What is This?

The driver wrapper provides a simple, unified interface for controlling RGB LED matrices on Raspberry Pi. It works with both real hardware and simulated displays, making it easy to develop and test without physical hardware.

## Key Features

✨ **Simple API** - Just 5 core methods: `set_pixel()`, `clear()`, `fill()`, `get_width()`, `get_height()`  
🎬 **Double-Buffering** - Smooth, tear-free animations with `create_frame_canvas()` and `swap_on_vsync()`  
🔄 **Hardware or Simulation** - Switch between real hardware and simulation with one line  
📝 **Well Documented** - Every function has clear documentation and examples  

## Installation

No installation needed! The driver wrapper uses the existing `rpi-rgb-led-matrix` library that should already be installed on your Raspberry Pi.

## Basic Usage

### Hello, LED Matrix!

```python
from drivers import create_driver

# Create a driver (False = simulation, True = hardware)
driver = create_driver(use_hardware=False, width=32, height=32)

# Set a single pixel to red
driver.set_pixel(10, 10, 255, 0, 0)

# Fill the entire matrix with blue
driver.fill(0, 0, 255)

# Clear everything
driver.clear()

print(f"Matrix size: {driver.get_width()}x{driver.get_height()}")
```

### Drawing a Simple Pattern

```python
from drivers import create_driver

driver = create_driver(use_hardware=False, width=32, height=32)

# Draw a red border
width = driver.get_width()
height = driver.get_height()

# Top and bottom
for x in range(width):
    driver.set_pixel(x, 0, 255, 0, 0)
    driver.set_pixel(x, height - 1, 255, 0, 0)

# Left and right
for y in range(height):
    driver.set_pixel(0, y, 255, 0, 0)
    driver.set_pixel(width - 1, y, 255, 0, 0)

print("Red border drawn!")
```

### Smooth Animation with Double-Buffering

The key to smooth, tear-free animations is double-buffering:

```python
import time
from drivers import create_driver

driver = create_driver(use_hardware=False, width=32, height=32)

# Create an offscreen canvas
canvas = driver.create_frame_canvas()

# Animation loop
x = 0
while x < 32:
    # Draw to the offscreen canvas
    canvas.clear()
    canvas.set_pixel(x, 16, 255, 0, 0)
    
    # Swap buffers atomically (prevents tearing!)
    canvas = driver.swap_on_vsync(canvas)
    
    x += 1
    time.sleep(0.05)

print("Animation complete!")
```

**Why double-buffering?**
- Prevents flicker and tearing
- Updates happen during vertical refresh
- Returns old canvas for reuse (no allocations)
- Same pattern works on hardware and simulation

## Switching to Hardware

When you're ready to run on real hardware, just change one line:

```python
# For simulation
driver = create_driver(use_hardware=False, width=32, height=32)

# For hardware
driver = create_driver(use_hardware=True, rows=32, cols=32, hardware_mapping="adafruit-hat")
```

Then run with sudo (required for GPIO access):
```bash
sudo python3 your_script.py
```

## Complete Example

Here's a complete bouncing ball animation:

```python
import time
from drivers import create_driver

# Toggle this to switch between hardware and simulation
USE_HARDWARE = False

# Create driver
driver = create_driver(use_hardware=USE_HARDWARE, width=32, height=32)

# Ball state
x, y = 16.0, 16.0
vx, vy = 0.5, 0.3

# Create offscreen canvas for double-buffering
canvas = driver.create_frame_canvas()

print("Press Ctrl+C to stop...")

try:
    while True:
        # Update position
        x += vx
        y += vy
        
        # Bounce off walls
        if x <= 0 or x >= 31:
            vx = -vx
        if y <= 0 or y >= 31:
            vy = -vy
        
        # Draw frame
        canvas.clear()
        canvas.set_pixel(int(x), int(y), 255, 0, 0)
        
        # Swap buffers
        canvas = driver.swap_on_vsync(canvas)
        
        time.sleep(0.02)
        
except KeyboardInterrupt:
    driver.clear()
    print("\nStopped!")
```

## Testing Your Code

Run the included test suite:
```bash
python3 test_driver.py
```

Try the example scripts:
```bash
python3 example_driver.py           # Basic features
python3 example_double_buffer.py    # Smooth animations
python3 sprinkles.py                # Random pixels
python3 stars.py                    # Pixel queue
```

## Common Patterns

### Pattern 1: Immediate Mode (Simple)
Good for static displays or simple effects:

```python
driver = create_driver(use_hardware=False)
driver.clear()
driver.set_pixel(10, 10, 255, 0, 0)
driver.set_pixel(11, 10, 0, 255, 0)
# Changes appear immediately
```

### Pattern 2: Double-Buffered Animation (Smooth)
Always use this for animations:

```python
driver = create_driver(use_hardware=False)
canvas = driver.create_frame_canvas()

while animating:
    canvas.clear()
    # Draw entire frame...
    canvas = driver.swap_on_vsync(canvas)  # Atomic swap
    time.sleep(0.02)
```

### Pattern 3: Brightness Control

```python
driver = create_driver(use_hardware=False)

# Set brightness (0-100)
driver.set_brightness(50)

# Get current brightness
brightness = driver.get_brightness()
print(f"Brightness: {brightness}%")
```

## Tips & Tricks

### 🎯 For Best Performance
1. **Reuse canvases**: `swap_on_vsync()` returns the old canvas - reuse it!
2. **Batch operations**: Draw the entire frame before swapping
3. **Use double-buffering**: Always for animations, prevents tearing
4. **Control frame rate**: Use `time.sleep()` to cap your frame rate

### 🐛 Debugging
1. **Start in simulation**: Set `use_hardware=False` to develop without hardware
2. **Check dimensions**: Call `get_width()` and `get_height()` to verify
3. **Inspect buffers**: In simulation, use `driver.get_buffer()` to see pixel values
4. **Test incrementally**: Start simple, add complexity gradually

### 🚀 Going Further
- Check out `example_double_buffer.py` for advanced animations
- Read the full API reference in `README.md`
- See implementation details in `DRIVER_IMPLEMENTATION.md`

## API Cheat Sheet

### Core Drawing (Canvas interface)
```python
driver.set_pixel(x, y, r, g, b)  # Set one pixel
driver.clear()                    # Clear to black
driver.fill(r, g, b)              # Fill with color
driver.get_width()                # Get width
driver.get_height()               # Get height
```

### Double-Buffering (MatrixDriver interface)
```python
canvas = driver.create_frame_canvas()       # Create offscreen buffer
canvas = driver.swap_on_vsync(canvas)       # Swap buffers, returns old
canvas = driver.swap_on_vsync(canvas, 2)    # With frame rate divisor
```

### Configuration
```python
driver.set_brightness(50)         # Set brightness (0-100)
brightness = driver.get_brightness()  # Get brightness
```

### Simulation-Only
```python
buffer = driver.get_buffer()      # Get 2D list of (r,g,b) tuples
```

## Next Steps

1. **Try the examples**: Run the provided example scripts to see the driver in action
2. **Read the docs**: Check out `README.md` for the complete API reference
3. **Build something**: Start with a simple pattern and expand from there
4. **Share your work**: The driver makes it easy to share code that works everywhere

## Getting Help

- **Examples**: Look at `example_driver.py` and `example_double_buffer.py`
- **Tests**: See `test_driver.py` for usage patterns
- **Documentation**: Full API reference in `README.md`
- **Implementation**: Deep dive in `DRIVER_IMPLEMENTATION.md`

## Summary

```python
# The essentials:
from drivers import create_driver

# 1. Create a driver
driver = create_driver(use_hardware=False)

# 2. For static content, use immediate mode
driver.set_pixel(10, 10, 255, 0, 0)

# 3. For animations, use double-buffering
canvas = driver.create_frame_canvas()
while True:
    canvas.clear()
    # Draw your frame...
    canvas = driver.swap_on_vsync(canvas)
```

Happy coding! 🎨✨