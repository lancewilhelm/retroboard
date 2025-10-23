"""
RGB Matrix Driver Wrapper

This module provides a simple abstraction layer over the RGBMatrix hardware driver.
By wrapping the core matrix functions, we can easily swap between the real hardware
implementation and a simulated web-based emulator without changing application code.

The driver exposes only the essential functions needed to control the LED matrix,
keeping the interface minimal and easy to implement across different backends.

Supports double-buffering via FrameCanvas for smooth, tear-free animations.
"""

from abc import ABC, abstractmethod
from rgbmatrix import RGBMatrix, RGBMatrixOptions, FrameCanvas as HardwareFrameCanvas


class Canvas(ABC):
    """
    Abstract base class for canvas objects (both main display and frame buffers).

    A canvas represents a drawable surface. The main matrix implements this,
    as do offscreen frame buffers used for double-buffering.
    """

    @abstractmethod
    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        """
        Set a single pixel to the specified RGB color.

        Args:
            x: X coordinate (0-indexed from left)
            y: Y coordinate (0-indexed from top)
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear the entire canvas by setting all pixels to black (0, 0, 0).
        """
        pass

    @abstractmethod
    def fill(self, r: int, g: int, b: int) -> None:
        """
        Fill the entire canvas with a single color.

        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        pass

    @abstractmethod
    def get_width(self) -> int:
        """
        Get the width of the canvas in pixels.

        Returns:
            Width in pixels
        """
        pass

    @abstractmethod
    def get_height(self) -> int:
        """
        Get the height of the canvas in pixels.

        Returns:
            Height in pixels
        """
        pass


class MatrixDriver(Canvas):
    """
    Abstract base class for RGB matrix drivers.

    This interface defines the core operations that any matrix driver
    (hardware or emulated) must implement. By coding against this interface,
    applications can work with both real hardware and simulators.

    Inherits from Canvas, adding driver-specific functionality like
    canvas creation and swapping for double-buffering.
    """

    @abstractmethod
    def create_frame_canvas(self) -> "FrameCanvasWrapper":
        """
        Create an offscreen frame buffer for double-buffering.

        This allows you to draw to an offscreen buffer and then swap it
        with the displayed frame atomically, preventing tearing and flicker.

        Returns:
            FrameCanvasWrapper instance for drawing offscreen

        Example:
            canvas = driver.create_frame_canvas()
            canvas.clear()
            canvas.set_pixel(10, 10, 255, 0, 0)
            canvas = driver.update(canvas)
        """
        pass

    @abstractmethod
    def update(
        self, canvas: "FrameCanvasWrapper", framerate_fraction: int = 1
    ) -> "FrameCanvasWrapper":
        """
        Atomically swap the offscreen canvas with the displayed frame.

        This swaps during the vertical refresh, preventing tearing. The
        previously displayed canvas is returned so you can reuse it for
        the next frame.

        Args:
            canvas: The offscreen canvas to display
            framerate_fraction: Framerate divisor for animation timing.
                              Default 1 = swap immediately on next frame.
                              Higher values slow down the swap rate.

        Returns:
            The previous canvas, ready for reuse

        Example:
            # Double-buffering loop
            canvas = driver.create_frame_canvas()
            while True:
                canvas.clear()
                # Draw your frame...
                canvas = driver.update(canvas)
        """
        pass

    @abstractmethod
    def get_brightness(self) -> int:
        """
        Get the current brightness level.

        Returns:
            Brightness value (0-100)
        """
        pass

    @abstractmethod
    def set_brightness(self, brightness: int) -> None:
        """
        Set the brightness level.

        Args:
            brightness: Brightness value (0-100)
        """
        pass


class HardwareFrameCanvasWrapper(Canvas):
    """
    Wrapper for hardware FrameCanvas objects.

    Provides a consistent interface for offscreen frame buffers that matches
    our Canvas abstraction.
    """

    def __init__(self, hardware_canvas: HardwareFrameCanvas):
        """
        Initialize the wrapper around a hardware FrameCanvas.

        Args:
            hardware_canvas: The underlying hardware FrameCanvas object
        """
        self._canvas = hardware_canvas

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        """Set a pixel on the frame canvas."""
        self._canvas.SetPixel(x, y, r, g, b)

    def clear(self) -> None:
        """Clear the frame canvas."""
        self._canvas.Clear()

    def fill(self, r: int, g: int, b: int) -> None:
        """Fill the frame canvas with a color."""
        self._canvas.Fill(r, g, b)

    def get_width(self) -> int:
        """Get canvas width."""
        return self._canvas.width

    def get_height(self) -> int:
        """Get canvas height."""
        return self._canvas.height


class HardwareDriver(MatrixDriver):
    """
    Hardware implementation of the MatrixDriver using the rpi-rgb-led-matrix library.

    This driver communicates with the actual RGB LED matrix hardware via the
    RGBMatrix library. It wraps the hardware-specific implementation to match
    our simplified driver interface.

    Supports double-buffering via create_frame_canvas() and update().
    """

    def __init__(
        self,
        rows: int = 32,
        cols: int = 64,
        hardware_mapping: str = "adafruit-hat",
        options: RGBMatrixOptions | None = None,
    ):
        """
        Initialize the hardware driver with matrix configuration.

        Args:
            rows: Number of rows in the LED matrix (default: 32)
            cols: Number of columns in the LED matrix (default: 64)
            hardware_mapping: Hardware adapter mapping (default: "adafruit-hat")
            options: Optional pre-configured RGBMatrixOptions object.
                    If provided, rows/cols/hardware_mapping are ignored.
        """
        if options is None:
            # Create default options with provided parameters
            options = RGBMatrixOptions()
            options.rows = rows
            options.cols = cols
            options.hardware_mapping = hardware_mapping

        # Initialize the underlying RGBMatrix hardware interface
        self._matrix = RGBMatrix(options=options)

        # Store dimensions for quick access
        self._width = self._matrix.width
        self._height = self._matrix.height

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        """
        Set a single pixel on the hardware matrix.

        Args:
            x: X coordinate (0-indexed from left)
            y: Y coordinate (0-indexed from top)
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        self._matrix.SetPixel(x, y, r, g, b)

    def clear(self) -> None:
        """
        Clear the hardware matrix by setting all pixels to black.
        """
        self._matrix.Clear()

    def fill(self, r: int, g: int, b: int) -> None:
        """
        Fill the entire hardware matrix with a single color.

        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        self._matrix.Fill(r, g, b)

    def get_width(self) -> int:
        """
        Get the width of the hardware matrix.

        Returns:
            Width in pixels
        """
        return self._width

    def get_height(self) -> int:
        """
        Get the height of the hardware matrix.

        Returns:
            Height in pixels
        """
        return self._height

    def create_frame_canvas(self) -> HardwareFrameCanvasWrapper:
        """
        Create an offscreen frame buffer for hardware double-buffering.

        Returns:
            HardwareFrameCanvasWrapper wrapping the hardware frame buffer
        """
        hardware_canvas = self._matrix.CreateFrameCanvas()
        return HardwareFrameCanvasWrapper(hardware_canvas)

    def update(
        self, canvas: HardwareFrameCanvasWrapper, framerate_fraction: int = 1
    ) -> HardwareFrameCanvasWrapper:
        """
        Swap the hardware frame buffer with the displayed frame.

        Args:
            canvas: The offscreen canvas to display
            framerate_fraction: Framerate divisor (default: 1)

        Returns:
            New canvas wrapper with the previous frame buffer
        """
        new_hardware_canvas = self._matrix.SwapOnVSync(
            canvas._canvas, framerate_fraction
        )
        return HardwareFrameCanvasWrapper(new_hardware_canvas)

    def get_brightness(self) -> int:
        """
        Get the current brightness of the hardware matrix.

        Returns:
            Brightness value (0-100)
        """
        return self._matrix.brightness

    def set_brightness(self, brightness: int) -> None:
        """
        Set the brightness of the hardware matrix.

        Args:
            brightness: Brightness value (0-100)
        """
        self._matrix.brightness = brightness


class SimulatedFrameCanvasWrapper(Canvas):
    """
    Simulated frame canvas for offscreen drawing.

    Maintains its own buffer that can be swapped with the main display buffer.
    """

    def __init__(self, width: int, height: int):
        """
        Initialize a simulated frame canvas.

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        self._width = width
        self._height = height
        self._buffer = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        """Set a pixel on the frame canvas."""
        if 0 <= x < self._width and 0 <= y < self._height:
            self._buffer[y][x] = (r, g, b)

    def clear(self) -> None:
        """Clear the frame canvas."""
        self._buffer = [
            [(0, 0, 0) for _ in range(self._width)] for _ in range(self._height)
        ]

    def fill(self, r: int, g: int, b: int) -> None:
        """Fill the frame canvas with a color."""
        self._buffer = [
            [(r, g, b) for _ in range(self._width)] for _ in range(self._height)
        ]

    def get_width(self) -> int:
        """Get canvas width."""
        return self._width

    def get_height(self) -> int:
        """Get canvas height."""
        return self._height

    def get_buffer(self) -> list:
        """
        Get the buffer contents (simulated driver specific).

        Returns:
            2D list of (r, g, b) tuples
        """
        return self._buffer


class SimulatedDriver(MatrixDriver):
    """
    Simulated implementation of the MatrixDriver for testing and web emulation.

    This driver maintains an in-memory representation of the matrix state
    without requiring actual hardware. It can be extended to send updates
    to a web-based visualizer via websockets or HTTP.

    Supports double-buffering with simulated frame canvases and buffer swapping.

    Note: This is a basic implementation. Web connectivity will be added later.
    """

    def __init__(self, width: int = 64, height: int = 32):
        """
        Initialize the simulated driver with specified dimensions.

        Args:
            width: Width of the simulated matrix (default: 64)
            height: Height of the simulated matrix (default: 32)
        """
        self._width = width
        self._height = height

        # Create a 2D array to store RGB values for each pixel
        # Each pixel is stored as a tuple (r, g, b)
        self._buffer = [[(0, 0, 0) for _ in range(width)] for _ in range(height)]

        # Brightness setting
        self._brightness = 100

    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        """
        Set a single pixel in the simulated matrix buffer.

        Args:
            x: X coordinate (0-indexed from left)
            y: Y coordinate (0-indexed from top)
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        # Bounds check to prevent index errors
        if 0 <= x < self._width and 0 <= y < self._height:
            self._buffer[y][x] = (r, g, b)

    def clear(self) -> None:
        """
        Clear the simulated matrix by setting all pixels to black.
        """
        self._buffer = [
            [(0, 0, 0) for _ in range(self._width)] for _ in range(self._height)
        ]

    def fill(self, r: int, g: int, b: int) -> None:
        """
        Fill the entire simulated matrix with a single color.

        Args:
            r: Red value (0-255)
            g: Green value (0-255)
            b: Blue value (0-255)
        """
        self._buffer = [
            [(r, g, b) for _ in range(self._width)] for _ in range(self._height)
        ]

    def get_width(self) -> int:
        """
        Get the width of the simulated matrix.

        Returns:
            Width in pixels
        """
        return self._width

    def get_height(self) -> int:
        """
        Get the height of the simulated matrix.

        Returns:
            Height in pixels
        """
        return self._height

    def get_buffer(self) -> list:
        """
        Get the current state of the simulated matrix buffer.

        This method is specific to the simulated driver and allows
        external systems (like a web visualizer) to read the current
        matrix state.

        Returns:
            2D list of (r, g, b) tuples representing the current matrix state
        """
        return self._buffer

    def create_frame_canvas(self) -> SimulatedFrameCanvasWrapper:
        """
        Create an offscreen frame buffer for simulated double-buffering.

        Returns:
            SimulatedFrameCanvasWrapper for offscreen drawing
        """
        return SimulatedFrameCanvasWrapper(self._width, self._height)

    def update(
        self, canvas: SimulatedFrameCanvasWrapper, framerate_fraction: int = 1
    ) -> SimulatedFrameCanvasWrapper:
        """
        Swap the simulated frame buffer with the display buffer.

        This copies the offscreen canvas buffer to the main display buffer,
        then returns a new canvas with the old display buffer contents.

        Args:
            canvas: The offscreen canvas to display
            framerate_fraction: Ignored in simulation (for API compatibility)

        Returns:
            New canvas with the previous display buffer contents
        """
        # Create new canvas with old display contents
        old_canvas = SimulatedFrameCanvasWrapper(self._width, self._height)
        old_canvas._buffer = [row[:] for row in self._buffer]  # Deep copy

        # Copy new canvas to display
        self._buffer = [row[:] for row in canvas._buffer]  # Deep copy

        return old_canvas

    def get_brightness(self) -> int:
        """
        Get the current simulated brightness.

        Returns:
            Brightness value (0-100)
        """
        return self._brightness

    def set_brightness(self, brightness: int) -> None:
        """
        Set the simulated brightness.

        Args:
            brightness: Brightness value (0-100)
        """
        self._brightness = max(0, min(100, brightness))


# Type alias for either frame canvas wrapper type
FrameCanvasWrapper = HardwareFrameCanvasWrapper | SimulatedFrameCanvasWrapper


def create_driver(use_hardware: bool = True, **kwargs) -> MatrixDriver:
    """
    Factory function to create the appropriate driver based on runtime configuration.

    This function simplifies driver instantiation by selecting between hardware
    and simulated drivers based on a boolean flag. Additional configuration
    parameters are passed through to the selected driver.

    Args:
        use_hardware: If True, create a HardwareDriver; if False, create a SimulatedDriver
        **kwargs: Additional keyword arguments to pass to the driver constructor
                 (e.g., rows, cols, width, height, hardware_mapping)

    Returns:
        MatrixDriver instance (either HardwareDriver or SimulatedDriver)

    Example:
        # Create hardware driver with default settings
        driver = create_driver(use_hardware=True)

        # Create simulated driver with custom dimensions
        driver = create_driver(use_hardware=False, width=64, height=32)

        # Create hardware driver with custom configuration
        driver = create_driver(use_hardware=True, rows=32, cols=64)
    """
    if use_hardware:
        return HardwareDriver(**kwargs)
    else:
        return SimulatedDriver(**kwargs)
