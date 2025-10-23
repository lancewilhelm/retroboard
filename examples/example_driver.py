"""
Example script demonstrating the use of the driver wrapper.

This script shows how to use both the HardwareDriver and SimulatedDriver
through the common MatrixDriver interface. The same code works with both
drivers, making it easy to develop and test without hardware.
"""

import time
from random import randrange
from drivers import create_driver, SimulatedDriver


def draw_random_pixels(driver, count=100, delay=0.01):
    """
    Draw random colored pixels on the matrix.

    Args:
        driver: MatrixDriver instance to draw on
        count: Number of random pixels to draw
        delay: Delay in seconds between each pixel
    """
    width = driver.get_width()
    height = driver.get_height()

    for _ in range(count):
        # Generate random position and color
        x = randrange(width)
        y = randrange(height)
        r = randrange(256)
        g = randrange(256)
        b = randrange(256)

        # Set the pixel
        driver.set_pixel(x, y, r, g, b)
        time.sleep(delay)


def draw_gradient(driver):
    """
    Draw a color gradient across the matrix.

    Args:
        driver: MatrixDriver instance to draw on
    """
    width = driver.get_width()
    height = driver.get_height()

    for y in range(height):
        for x in range(width):
            # Create a gradient from red to blue horizontally
            r = int(255 * (1 - x / width))
            g = 0
            b = int(255 * (x / width))

            driver.set_pixel(x, y, r, g, b)


def main():
    """
    Main demonstration function.
    """
    # Toggle this to switch between hardware and simulated driver
    # Set to False to run without hardware (for testing)
    USE_HARDWARE = True

    # Create the driver using the factory function
    print(f"Creating {'hardware' if USE_HARDWARE else 'simulated'} driver...")
    driver = create_driver(use_hardware=USE_HARDWARE, rows=32, cols=32)

    print(f"Matrix dimensions: {driver.get_width()}x{driver.get_height()}")

    try:
        # Example 1: Fill with a solid color
        print("Filling matrix with red...")
        driver.fill(255, 0, 0)
        time.sleep(1)

        print("Filling matrix with green...")
        driver.fill(0, 255, 0)
        time.sleep(1)

        print("Filling matrix with blue...")
        driver.fill(0, 0, 255)
        time.sleep(1)

        # Example 2: Clear the matrix
        print("Clearing matrix...")
        driver.clear()
        time.sleep(1)

        # Example 3: Draw a gradient
        print("Drawing gradient...")
        draw_gradient(driver)
        time.sleep(2)

        # Example 4: Draw random pixels
        print("Drawing random pixels...")
        driver.clear()
        draw_random_pixels(driver, count=200, delay=0.01)
        time.sleep(1)

        # If using simulated driver, print the buffer state
        if isinstance(driver, SimulatedDriver):
            print("\nSimulated driver buffer (first row):")
            buffer = driver.get_buffer()
            print(buffer[0][:5])  # Print first 5 pixels of first row

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    finally:
        # Clean up: clear the matrix
        print("Clearing matrix before exit...")
        driver.clear()


if __name__ == "__main__":
    main()
