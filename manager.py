"""
Application Manager for LED Matrix.

Manages the lifecycle of matrix applications, handles switching between apps,
and processes commands from the API.
"""

import time
import queue
import logging
from typing import Optional, Dict, Type
from apps import MatrixApplication

logger = logging.getLogger(__name__)


class ApplicationManager:
    """
    Manages matrix applications.
    
    Handles:
    - Running the current application
    - Switching between applications
    - Processing commands from the API
    - Graceful app lifecycle management
    """
    
    def __init__(self, driver):
        """
        Initialize the application manager.
        
        Args:
            driver: MatrixDriver instance
        """
        self.driver = driver
        self.current_app: Optional[MatrixApplication] = None
        self.current_app_name: Optional[str] = None
        self.available_apps: Dict[str, Type[MatrixApplication]] = {}
        self.command_queue = queue.Queue()
        self.running = False
    
    def register_app(self, name: str, app_class: Type[MatrixApplication]):
        """
        Register an application.
        
        Args:
            name: Unique name for the app
            app_class: MatrixApplication subclass
        """
        self.available_apps[name] = app_class
        logger.info(f"Registered app: {name}")
    
    def start_app(self, name: str, config: Optional[Dict] = None) -> bool:
        """
        Start an application.
        
        Args:
            name: Name of the app to start
            config: Optional configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if name not in self.available_apps:
            logger.error(f"App not found: {name}")
            return False
        
        # Stop current app if running
        if self.current_app:
            self.stop_current_app()
        
        try:
            # Create and setup the app
            app_class = self.available_apps[name]
            self.current_app = app_class(self.driver, config or {})
            self.current_app.setup()
            self.current_app_name = name
            logger.info(f"Started app: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start app {name}: {e}")
            self.current_app = None
            self.current_app_name = None
            return False
    
    def stop_current_app(self):
        """Stop the currently running application."""
        if self.current_app:
            try:
                logger.info(f"Stopping app: {self.current_app_name}")
                self.current_app.stop()
                self.current_app.cleanup()
            except Exception as e:
                logger.error(f"Error stopping app: {e}")
            finally:
                self.current_app = None
                self.current_app_name = None
    
    def switch_app(self, name: str, config: Optional[Dict] = None) -> bool:
        """
        Switch to a different application.
        
        Args:
            name: Name of the app to switch to
            config: Optional configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        return self.start_app(name, config)
    
    def get_current_app_name(self) -> Optional[str]:
        """Get the name of the currently running app."""
        return self.current_app_name
    
    def get_available_apps(self) -> list:
        """Get list of available app names."""
        return list(self.available_apps.keys())
    
    def process_commands(self):
        """Process any pending commands from the API."""
        while not self.command_queue.empty():
            try:
                command = self.command_queue.get_nowait()
                action = command.get('action')
                
                if action == 'switch':
                    app_name = command.get('app')
                    config = command.get('config', {})
                    self.switch_app(app_name, config)
                
                elif action == 'stop':
                    self.stop_current_app()
                
                elif action == 'config':
                    if self.current_app:
                        key = command.get('key')
                        value = command.get('value')
                        self.current_app.update_config(key, value)
                
                elif action == 'quit':
                    self.running = False
                    
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error processing command: {e}")
    
    def run(self):
        """
        Main loop - runs the current application.
        
        This should be called from the main thread. It will:
        1. Process commands from the API
        2. Run one iteration of the current app
        3. Sleep briefly to prevent CPU spinning
        """
        self.running = True
        logger.info("Application manager started")
        
        try:
            while self.running:
                # Process any API commands
                self.process_commands()
                
                # Run current app if one is active
                if self.current_app:
                    try:
                        self.current_app.loop()
                    except Exception as e:
                        logger.error(f"Error in app loop: {e}")
                        # Stop the crashed app
                        self.stop_current_app()
                else:
                    # No app running, just sleep
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            # Clean shutdown
            if self.current_app:
                self.stop_current_app()
            logger.info("Application manager stopped")
    
    def queue_command(self, command: Dict):
        """
        Queue a command for processing.
        
        Args:
            command: Command dictionary with 'action' key
        """
        self.command_queue.put(command)
