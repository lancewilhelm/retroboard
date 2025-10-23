"""
Digital clock application for LED matrix.

Displays the current time in HH:MM:SS format.
"""

import time
from datetime import datetime
from drivers import BDFFont
from apps.base import MatrixApplication


class ClockApp(MatrixApplication):
    """
    Digital clock that displays current time.

    Config options:
        font: BDF font file name (default: "tom-thumb")
        color: RGB tuple for text color (default: cyan)
    """

    def setup(self):
        """Initialize the clock application."""
        # Get configuration
        font = self.config.get("font", "tom-thumb")
        self.color = self.config.get("color", (255, 255, 255))

        # Load font
        self.font = BDFFont(f"./drivers/text/fonts/{font}.bdf")

        # Get matrix dimensions
        self.width = self.driver.get_width()
        self.height = self.driver.get_height()

        # Create canvas for double-buffering
        self.driver.clear()
        self.canvas = self.driver.create_frame_canvas()

        # Track last update time to avoid unnecessary redraws
        self.last_second = -1

    def loop(self):
        """Draw one frame of the clock."""
        # Get current time
        now = datetime.now()
        current_second = now.second

        # Only update if the second has changed
        if current_second != self.last_second:
            self.last_second = current_second
            time_string = now.strftime("%H:%M:%S")

            # Clear canvas
            self.canvas.clear()

            # Calculate centered position
            text_width = self.font.get_text_width(time_string)
            x_pos = (self.width - text_width) // 2
            y_pos = (self.height + self.font.height()) // 2

            # Draw the time
            self.font.draw_text(
                self.canvas,
                x_pos,
                y_pos,
                time_string,
                self.color[0],
                self.color[1],
                self.color[2],
            )

            # Update display
            self.canvas = self.driver.update(self.canvas)

        # Sleep briefly to prevent CPU spinning
        time.sleep(0.1)

    def update_config(self, key, value):
        """Handle configuration changes."""
        super().update_config(key, value)

        if key == "color":
            self.color = value
        elif key == "font":
            self.font = BDFFont(f"./drivers/text/fonts/{value}.bdf")
