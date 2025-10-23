"""
Digital clock display - shows current time on the LED matrix.

This example displays a digital clock using the driver wrapper and our custom
text rendering library. It works with both hardware and simulated displays.
The clock updates every second and shows the time in HH:MM:SS format.
"""

import time
import math
from datetime import datetime
from drivers import create_driver, BDFFont

# Toggle between hardware and simulated driver
# Set to False to test without hardware
USE_HARDWARE = True
FRAME_RATE = 60

# Create the driver using the factory function
driver = create_driver(
    use_hardware=USE_HARDWARE, rows=32, cols=64, hardware_mapping="adafruit-hat"
)

# Get matrix dimensions
width = driver.get_width()
height = driver.get_height()

print(f"Running clock on {width}x{height} matrix")
print(f"Using {'hardware' if USE_HARDWARE else 'simulated'} driver")

# Load font using our custom BDF font loader
font = BDFFont("./drivers/text/fonts/5x7.bdf")

# Start with a clear canvas
driver.clear()
canvas = driver.create_frame_canvas()


def rainbowSine(t):
    a = 2 * math.pi * (t - math.floor(t))
    r = 0.5 * (math.sin(a) + 1)
    g = 0.5 * (math.sin(a - 2 * math.pi / 3) + 1)
    b = 0.5 * (math.sin(a - 4 * math.pi / 3) + 1)
    return [round(r * 255), round(g * 255), round(b * 255)]


try:
    while True:
        # Get current time
        now = datetime.now()
        time_string = now.strftime("%H:%M:%S")

        # Clear the offscreen canvas
        canvas.clear()

        # Calculate text position to center it
        text_width = font.get_text_width(time_string)
        x_pos = (width - text_width) // 2
        y_pos = (height + font.height()) // 2

        # Draw the time text using our custom renderer
        # This works with both hardware and simulated drivers!
        text_r, text_g, text_b = rainbowSine((time.time() % 60) / 60)
        font.draw_text(canvas, x_pos, y_pos, time_string, text_r, text_g, text_b)

        # Swap the canvas on vertical sync
        canvas = driver.update(canvas)

        # Update once per second
        time.sleep(1 / FRAME_RATE)

except KeyboardInterrupt:
    print("\nClock stopped!")
    driver.clear()
