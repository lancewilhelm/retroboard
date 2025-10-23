"""
Scrolling text application for LED matrix.

Displays text scrolling from right to left across the display.
"""

import time
from drivers import BDFFont
from apps.base import MatrixApplication


class ScrollTextApp(MatrixApplication):
    """
    Scrolling text display.

    Config options:
        text: Text to display (default: "Hello, World!")
        font: BDF font file name (default: "tom-thumb")
        color: RGB tuple for text color (default: cyan)
        speed: Scroll speed in pixels per frame (default: 1)
        fps: Frames per second (default: 30)
    """

    def setup(self):
        """Initialize the scrolling text application."""
        # Get configuration
        self.text = self.config.get("text", "Hello, World!")
        font = self.config.get("font", "tom-thumb")
        self.color = self.config.get("color", (255, 255, 255))
        self.speed = self.config.get("speed", 1)
        fps = self.config.get("fps", 30)
        self.frame_delay = 1.0 / fps

        # Load font
        self.font = BDFFont(f"./drivers/text/fonts/{font}.bdf")

        # Get matrix dimensions
        self.width = self.driver.get_width()
        self.height = self.driver.get_height()

        # Calculate text width
        self.text_width = self.font.get_text_width(self.text)

        # Start position (off screen to the right)
        self.x_pos = self.width

        # Y position (vertically centered)
        self.y_pos = (self.height + self.font.height()) // 2

        # Create canvas for double-buffering
        self.driver.clear()
        self.canvas = self.driver.create_frame_canvas()

    def loop(self):
        """Draw one frame of scrolling text."""
        # Clear canvas
        self.canvas.clear()

        # Draw text at current position
        self.font.draw_text(
            self.canvas,
            self.x_pos,
            self.y_pos,
            self.text,
            self.color[0],
            self.color[1],
            self.color[2],
        )

        # Update display
        self.canvas = self.driver.update(self.canvas)

        # Move text left
        self.x_pos -= self.speed

        # Reset position when text scrolls completely off screen
        if self.x_pos < -self.text_width:
            self.x_pos = self.width

        # Control frame rate
        time.sleep(self.frame_delay)

    def update_config(self, key, value):
        """Handle configuration changes."""
        super().update_config(key, value)

        if key == "text":
            self.text = value
            self.text_width = self.font.get_text_width(self.text)
        elif key == "color":
            self.color = value
        elif key == "speed":
            self.speed = value
        elif key == "fps":
            self.frame_delay = 1.0 / value
        elif key == "font":
            self.font = BDFFont(f"./drivers/text/fonts/{value}.bdf")
            self.text_width = self.font.get_text_width(self.text)
