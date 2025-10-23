"""
Base class for matrix applications.

All applications that run on the LED matrix should inherit from MatrixApplication
and implement the setup(), loop(), and cleanup() methods.
"""

from abc import ABC, abstractmethod


class MatrixApplication(ABC):
    """
    Base class for all matrix applications.
    
    Applications implement a simple lifecycle:
    1. setup() - Called once when app starts
    2. loop() - Called repeatedly (one frame/iteration)
    3. cleanup() - Called once when app stops
    """
    
    def __init__(self, driver, config=None):
        """
        Initialize the application.
        
        Args:
            driver: MatrixDriver instance to draw on
            config: Dictionary of configuration options (optional)
        """
        self.driver = driver
        self.config = config or {}
        self._stop_flag = False
        self.canvas = None
    
    @abstractmethod
    def setup(self):
        """
        Initialize the application.
        
        Called once when the app starts. Use this to:
        - Load fonts
        - Create canvases
        - Initialize state variables
        - Set up any resources
        """
        pass
    
    @abstractmethod
    def loop(self):
        """
        Execute one iteration of the application.
        
        Called repeatedly by the ApplicationManager. This should:
        - Draw one frame
        - Update state
        - Return quickly (don't block for long periods)
        
        Check should_stop() periodically if doing long operations.
        """
        pass
    
    def cleanup(self):
        """
        Clean up resources when stopping.
        
        Called once when the app is stopping. Use this to:
        - Clear the display
        - Release resources
        - Save state if needed
        
        Default implementation clears the display.
        """
        self.driver.clear()
    
    def should_stop(self):
        """
        Check if the application should stop.
        
        Returns:
            True if the app should stop, False otherwise
        """
        return self._stop_flag
    
    def stop(self):
        """
        Request the application to stop.
        
        Sets the stop flag. The app should check should_stop()
        and exit gracefully.
        """
        self._stop_flag = True
    
    def get_config(self):
        """
        Get the current configuration.
        
        Returns:
            Dictionary of current configuration values
        """
        return self.config.copy()
    
    def update_config(self, key, value):
        """
        Update a configuration value.
        
        Apps can override this to handle config changes dynamically.
        
        Args:
            key: Configuration key to update
            value: New value
        """
        self.config[key] = value
