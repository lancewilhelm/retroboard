"""
Scrolling text example - demonstrates text rendering with animation.

This example shows text scrolling across the LED matrix from right to left,
demonstrating how our custom text library can be used for dynamic effects.
"""

import time
from drivers import create_driver, BDFFont

# Toggle between hardware and simulated driver
USE_HARDWARE = True
FRAME_RATE = 24

# Create the driver
if USE_HARDWARE:
    driver = create_driver(
        use_hardware=True, rows=32, cols=64, hardware_mapping="adafruit-hat"
    )
else:
    driver = create_driver(use_hardware=False, width=64, height=32)

# Get matrix dimensions
width = driver.get_width()
height = driver.get_height()

print(f"Running scrolling text on {width}x{height} matrix")
print(f"Using {'hardware' if USE_HARDWARE else 'simulated'} driver")
print("Press Ctrl+C to stop")

# Load font
font = BDFFont("./drivers/text/fonts/creep.bdf")

# Text to scroll
scroll_text = "Hello, World! This is scrolling text on an LED matrix!"

# Calculate text width
text_width = font.get_text_width(scroll_text)

# Starting position (off screen to the right)
x_pos = width

# Text color (cyan)
text_r, text_g, text_b = 155, 155, 155

# Y position (vertically centered)
y_pos = (height + font.height()) // 2

# Create canvas for double-buffering
driver.clear()
canvas = driver.create_frame_canvas()

try:
    while True:
        # Clear the canvas
        canvas.clear()

        # Draw the text at current position
        font.draw_text(canvas, x_pos, y_pos, scroll_text, text_r, text_g, text_b)

        # Update display
        canvas = driver.update(canvas)

        # Move text left
        x_pos -= 1

        # Reset position when text scrolls completely off screen
        if x_pos < -text_width:
            x_pos = width

        # Control scroll speed (higher = slower)
        time.sleep(1 / FRAME_RATE)

except KeyboardInterrupt:
    print("\nScrolling stopped!")
    driver.clear()
