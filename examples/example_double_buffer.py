"""
Double-buffering example demonstrating smooth, tear-free animations.

This example shows how to use create_frame_canvas() and swap_on_vsync()
to implement double-buffering for smooth animations without tearing or flicker.

The pattern is:
1. Create an offscreen canvas
2. Draw the next frame to the offscreen canvas
3. Swap it with swap_on_vsync(), which returns the old canvas
4. Repeat using the returned canvas
"""

import time
import math
from drivers import create_driver

# Toggle between hardware and simulated driver
USE_HARDWARE = True


def draw_bouncing_ball(driver):
    """
    Animate a bouncing ball using double-buffering.

    This demonstrates how double-buffering prevents tearing by drawing
    to an offscreen buffer and swapping it atomically.

    Args:
        driver: MatrixDriver instance
    """
    width = driver.get_width()
    height = driver.get_height()

    # Ball position and velocity
    x = float(width // 2)
    y = float(height // 2)
    vx = 0.5
    vy = 0.3
    radius = 2

    # Create the offscreen canvas for double-buffering
    canvas = driver.create_frame_canvas()

    print("Animating bouncing ball (press Ctrl+C to stop)...")
    frame_count = 0

    try:
        while True:
            # Clear the offscreen canvas
            canvas.clear()

            # Update ball position
            x += vx
            y += vy

            # Bounce off walls
            if x <= radius or x >= width - radius:
                vx = -vx
                x = max(radius, min(width - radius, x))

            if y <= radius or y >= height - radius:
                vy = -vy
                y = max(radius, min(height - radius, y))

            # Draw ball with a simple circle approximation
            cx = int(x)
            cy = int(y)

            # Color cycles through the rainbow
            hue = (frame_count * 2) % 360
            r, g, b = hsv_to_rgb(hue, 1.0, 1.0)

            # Draw pixels in a circular pattern
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if dx * dx + dy * dy <= radius * radius:
                        px = cx + dx
                        py = cy + dy
                        if 0 <= px < width and 0 <= py < height:
                            canvas.set_pixel(px, py, r, g, b)

            # Swap the offscreen canvas with the display
            # This happens during vsync, preventing tearing
            canvas = driver.swap_on_vsync(canvas)

            frame_count += 1
            time.sleep(0.02)  # ~50 FPS

    except KeyboardInterrupt:
        print(f"\nRendered {frame_count} frames")


def draw_rotating_square(driver):
    """
    Animate a rotating square using double-buffering.

    This demonstrates smooth rotation without flicker.

    Args:
        driver: MatrixDriver instance
    """
    width = driver.get_width()
    height = driver.get_height()

    center_x = width / 2.0
    center_y = height / 2.0
    size = min(width, height) * 0.4

    canvas = driver.create_frame_canvas()

    print("Animating rotating square (press Ctrl+C to stop)...")
    angle = 0

    try:
        while True:
            # Clear offscreen canvas
            canvas.clear()

            # Calculate rotation
            angle += 2
            rad = math.radians(angle)
            sin_a = math.sin(rad)
            cos_a = math.cos(rad)

            # Define square corners
            corners = [
                (-size, -size),
                (size, -size),
                (size, size),
                (-size, size),
            ]

            # Rotate and draw the square
            for i in range(4):
                x1, y1 = corners[i]
                x2, y2 = corners[(i + 1) % 4]

                # Rotate both points
                rx1 = x1 * cos_a - y1 * sin_a + center_x
                ry1 = x1 * sin_a + y1 * cos_a + center_y
                rx2 = x2 * cos_a - y2 * sin_a + center_x
                ry2 = x2 * sin_a + y2 * cos_a + center_y

                # Draw line between points
                draw_line(canvas, int(rx1), int(ry1), int(rx2), int(ry2), 255, 255, 255)

            # Swap buffers
            canvas = driver.swap_on_vsync(canvas)

            time.sleep(0.03)

    except KeyboardInterrupt:
        print("\nAnimation stopped")


def draw_smooth_gradient(driver):
    """
    Animate a smooth color gradient sweep.

    Args:
        driver: MatrixDriver instance
    """
    width = driver.get_width()
    height = driver.get_height()

    canvas = driver.create_frame_canvas()

    print("Animating gradient sweep (press Ctrl+C to stop)...")
    offset = 0

    try:
        while True:
            canvas.clear()

            # Draw gradient
            for y in range(height):
                for x in range(width):
                    # Create a moving gradient
                    value = (x + y + offset) % 256
                    r = value
                    g = 255 - value
                    b = (value + 128) % 256

                    canvas.set_pixel(x, y, r, g, b)

            canvas = driver.swap_on_vsync(canvas)

            offset = (offset + 2) % 256
            time.sleep(0.03)

    except KeyboardInterrupt:
        print("\nAnimation stopped")


def draw_line(canvas, x0, y0, x1, y1, r, g, b):
    """
    Draw a line using Bresenham's algorithm.

    Args:
        canvas: Canvas to draw on
        x0, y0: Start point
        x1, y1: End point
        r, g, b: RGB color
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        canvas.set_pixel(x0, y0, r, g, b)

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def hsv_to_rgb(h, s, v):
    """
    Convert HSV color to RGB.

    Args:
        h: Hue (0-360)
        s: Saturation (0-1)
        v: Value (0-1)

    Returns:
        Tuple of (r, g, b) values (0-255)
    """
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def main():
    """
    Main demonstration function.
    """
    print("Double-Buffering Animation Demo")
    print("=" * 50)

    # Create driver
    driver = create_driver(
        use_hardware=USE_HARDWARE, rows=32, cols=64, hardware_mapping="adafruit-hat"
    )

    print(f"Matrix: {driver.get_width()}x{driver.get_height()}")
    print(f"Mode: {'Hardware' if USE_HARDWARE else 'Simulated'}")
    print("=" * 50)

    # Clear the display first
    driver.clear()

    try:
        # Run different animations
        print("\n1. Bouncing Ball")
        print("-" * 50)
        draw_bouncing_ball(driver)

        # Uncomment to try other animations:
        # print("\n2. Rotating Suare")
        # print("-" * 50)
        # draw_rotating_square(driver)

        # print("\n3. Gradient Sweep")
        # print("-" * 50)
        # draw_smooth_gradient(driver)

    except KeyboardInterrupt:
        print("\n\nDemo interrupted")
    finally:
        # Clean up
        driver.clear()
        print("Display cleared")


if __name__ == "__main__":
    main()
