"""
Stars animation application for LED matrix.

Displays twinkling colored stars that fade in and out.
"""

import time
import math
from random import randrange
from dataclasses import dataclass
from apps.base import MatrixApplication


@dataclass
class Star:
    """Represents a single star on the display."""
    x: int
    y: int
    r: int
    g: int
    b: int
    age: int


class StarsApp(MatrixApplication):
    """
    Stars animation with fading colored pixels.
    
    Config options:
        spawn_rate: Number of stars to spawn per frame (default: 1)
        lifetime: How many frames a star lives (default: 40)
        fps: Frames per second (default: 60)
    """
    
    def setup(self):
        """Initialize the stars application."""
        # Get configuration
        self.spawn_rate = self.config.get('spawn_rate', 1)
        self.lifetime = self.config.get('lifetime', 40)
        fps = self.config.get('fps', 60)
        self.frame_delay = 1.0 / fps
        
        # Get matrix dimensions
        self.width = self.driver.get_width()
        self.height = self.driver.get_height()
        
        # Initialize star queue
        self.star_queue = []
        
        # Create canvas for double-buffering
        self.driver.clear()
        self.canvas = self.driver.create_frame_canvas()
    
    def loop(self):
        """Draw one frame of stars."""
        # Clear canvas
        self.canvas.clear()
        
        # Spawn new stars
        for _ in range(self.spawn_rate):
            # Random color
            r = randrange(256)
            g = randrange(256)
            b = randrange(256)
            
            # Random position
            x = randrange(self.width)
            y = randrange(self.height)
            
            # Add to queue
            self.star_queue.append(Star(x, y, r, g, b, 0))
        
        # Update and draw stars
        new_queue = []
        for star in self.star_queue:
            star.age += 1
            
            # Keep star if still alive
            if star.age <= self.lifetime:
                # Calculate fade phase (sine wave for smooth fade in/out)
                phase = math.sin(star.age / self.lifetime * math.pi)
                
                # Draw star with faded color
                self.canvas.set_pixel(
                    star.x, star.y,
                    int(star.r * phase),
                    int(star.g * phase),
                    int(star.b * phase)
                )
                
                new_queue.append(star)
        
        # Update star queue
        self.star_queue = new_queue
        
        # Update display
        self.canvas = self.driver.update(self.canvas)
        
        # Control frame rate
        time.sleep(self.frame_delay)
    
    def update_config(self, key, value):
        """Handle configuration changes."""
        super().update_config(key, value)
        
        if key == 'spawn_rate':
            self.spawn_rate = value
        elif key == 'lifetime':
            self.lifetime = value
        elif key == 'fps':
            self.frame_delay = 1.0 / value
