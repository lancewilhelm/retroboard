"""
Stars animation - maintains a fixed number of colored pixels on screen.

This example has been updated to use the driver wrapper, allowing it to
work with both hardware and simulated displays. The animation keeps track
of the most recent pixels and removes the oldest ones to maintain a
constant number of active pixels.
"""

import time
import math
from random import randrange
from drivers import create_driver
from dataclasses import dataclass


@dataclass
class Star:
    x: int
    y: int
    r: int
    g: int
    b: int
    age: int


# Toggle between hardware and simulated driver
# Set to False to test without hardware
USE_HARDWARE = True

# Create the driver using the factory function
driver = create_driver(
    use_hardware=USE_HARDWARE, rows=32, cols=64, hardware_mapping="adafruit-hat"
)

# Get matrix dimensions (works with any size)
width = driver.get_width()
height = driver.get_height()

print(f"Running stars animation on {width}x{height} matrix")
print(f"Using {'hardware' if USE_HARDWARE else 'simulated'} driver")

FRAME_RATE = 60  # Frames per second (int)
SPAWN_RATE = 1  # Number of stars to spawn per frame (int)
LIFETIME = 40  # Number of frames a star stays active (int)
star_queue: list[Star] = list()

# Start with a clear canvas
driver.clear()
canvas = driver.create_frame_canvas()

while True:
    # Clear the offscreen canvas
    canvas.clear()

    # Spawn new stars
    for _ in range(SPAWN_RATE):
        # Generate random RGB color
        r = randrange(256)
        g = randrange(256)
        b = randrange(256)
        # r = 255
        # g = 255
        # b = 255
        # dr = randrange(30)
        # dg = randrange(30)
        # db = randrange(30)
        # r = r - dr
        # g = g - dg
        # b = b - db

        # Generate random position
        x = randrange(width)
        y = randrange(height)

        # Set inital age to 0
        age = 0

        # Add the new star to the queue
        star_queue.append(Star(x, y, r, g, b, age))

    # Update the star queue and canvas
    new_queue: list[Star] = []
    for s in star_queue:
        s.age += 1
        if s.age <= LIFETIME:
            phase = math.sin(s.age / LIFETIME * math.pi)
            canvas.set_pixel(
                s.x, s.y, int(s.r * phase), int(s.g * phase), int(s.b * phase)
            )
            new_queue.append(s)
        else:
            canvas.set_pixel(s.x, s.y, 0, 0, 0)
    star_queue = new_queue

    # Swap the canvas on vertical sync
    canvas = driver.update(canvas)
    time.sleep(1 / FRAME_RATE)
