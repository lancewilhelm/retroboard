"""
Test the BDF font parser and text renderer.

This script tests our custom text rendering library with both hardware
and simulated drivers.
"""

import time
from drivers import create_driver, BDFFont

# Use simulation for testing (set to True for hardware)
USE_HARDWARE = False

# Create driver
driver = create_driver(use_hardware=USE_HARDWARE, width=64, height=32)

print(f"Testing text renderer on {driver.get_width()}x{driver.get_height()} matrix")
print(f"Using {'hardware' if USE_HARDWARE else 'simulated'} driver")

# Load a font
font = BDFFont("./rpi-rgb-led-matrix/fonts/6x10.bdf")
print(f"Font loaded! Height: {font.height()} pixels")

# Create canvas for double-buffering
canvas = driver.create_frame_canvas()

try:
    # Test 1: Draw "Hello!"
    print("\nTest 1: Drawing 'Hello!'")
    canvas.clear()
    font.draw_text(canvas, 2, 16, "Hello!", 255, 0, 0)  # Red text
    canvas = driver.update(canvas)
    time.sleep(2)
    
    # Test 2: Draw centered text
    print("Test 2: Drawing centered text")
    canvas.clear()
    text = "TEST"
    text_width = font.get_text_width(text)
    x = (driver.get_width() - text_width) // 2
    y = (driver.get_height() + font.height()) // 2
    font.draw_text(canvas, x, y, text, 0, 255, 0)  # Green text
    canvas = driver.update(canvas)
    time.sleep(2)
    
    # Test 3: Draw numbers
    print("Test 3: Drawing numbers")
    canvas.clear()
    font.draw_text(canvas, 4, 16, "12:34:56", 0, 255, 255)  # Cyan text
    canvas = driver.update(canvas)
    time.sleep(2)
    
    # Test 4: Different colors
    print("Test 4: Multiple lines, different colors")
    canvas.clear()
    font.draw_text(canvas, 2, 10, "ABC", 255, 0, 0)    # Red
    font.draw_text(canvas, 2, 20, "123", 0, 255, 0)    # Green
    font.draw_text(canvas, 2, 30, "XYZ", 0, 0, 255)    # Blue
    canvas = driver.update(canvas)
    time.sleep(2)
    
    # Test 5: Character spacing
    print("Test 5: Testing character spacing")
    canvas.clear()
    font.draw_text(canvas, 2, 12, "SPACED", 255, 255, 0, spacing=2)
    font.draw_text(canvas, 2, 24, "NORMAL", 255, 255, 0, spacing=0)
    canvas = driver.update(canvas)
    time.sleep(2)
    
    print("\nAll tests complete!")
    driver.clear()

except KeyboardInterrupt:
    print("\nTest interrupted!")
    driver.clear()
except Exception as e:
    print(f"\nError during test: {e}")
    import traceback
    traceback.print_exc()
    driver.clear()
