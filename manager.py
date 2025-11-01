"""
Application Manager for LED Matrix.

Manages the lifecycle of matrix applications, handles switching between apps,
and processes commands from the API.
"""

import time
import queue
import logging
import json
import os
from typing import Optional, Dict, Type, Tuple, List
from apps import MatrixApplication

logger = logging.getLogger(__name__)

# Default state file location
STATE_FILE = "state.json"


class ApplicationManager:
    """
    Manages matrix applications.

    Handles:
    - Running the current application
    - Switching between applications
    - Processing commands from the API
    - Graceful app lifecycle management
    """

    def __init__(self, driver, state_file: str = STATE_FILE):
        """
        Initialize the application manager.

        Args:
            driver: MatrixDriver instance
            state_file: Path to state persistence file
        """
        self.driver = driver
        self.current_app: Optional[MatrixApplication] = None
        self.current_app_name: Optional[str] = None
        self.available_apps: Dict[str, Type[MatrixApplication]] = {}
        self.command_queue = queue.Queue()
        self.running = False
        self.state_file = state_file
        self.app_configs: Dict[str, Dict] = {}  # Stores last known config for each app
        self.settings: Dict = {}  # Stores global settings (brightness, etc.)

        # Carousel mode settings
        self.carousel_enabled = False
        self.carousel_apps: List[Dict] = []  # List of {app: str, duration: int}
        self.carousel_index = 0
        self.carousel_timer = 0
        self.last_carousel_time = time.time()

        # WebSocket support (set by API)
        self.socketio = None

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

            # Emit WebSocket event
            self._emit_current_app()

            return True

        except Exception as e:
            logger.error(f"Failed to start app {name}: {e}")
            self.current_app = None
            self.current_app_name = None
            return False

    def stop_current_app(self, save_state: bool = False):
        """
        Stop the currently running application.

        Args:
            save_state: If True, saves state after stopping (user-initiated stop).
                       If False, only cleans up without saving (e.g., shutdown).
        """
        if self.current_app:
            try:
                logger.info(f"Stopping app: {self.current_app_name}")
                # Save current config before stopping
                if self.current_app_name:
                    self.app_configs[self.current_app_name] = (
                        self.current_app.get_config()
                    )
                self.current_app.stop()
                self.current_app.cleanup()
            except Exception as e:
                logger.error(f"Error stopping app: {e}")
            finally:
                # Only clear current app name if this is a user-initiated stop
                if save_state:
                    self.current_app = None
                    self.current_app_name = None
                    self.save_state()

                    # Emit WebSocket event
                    self._emit_current_app()
                else:
                    # Shutdown - just clean up, don't clear app name or save
                    self.current_app = None

    def switch_app(self, name: str, config: Optional[Dict] = None) -> bool:
        """
        Switch to a different application.

        Args:
            name: Name of the app to switch to
            config: Optional configuration dictionary

        Returns:
            True if successful, False otherwise
        """
        success = self.start_app(name, config)
        if success:
            # Save state after successful switch
            if self.current_app_name:
                self.app_configs[self.current_app_name] = self.current_app.get_config()
            self.save_state()
        return success

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
                action = command.get("action")

                if action == "switch":
                    app_name = command.get("app")
                    config = command.get("config", {})
                    self.switch_app(app_name, config)

                elif action == "stop":
                    # User-initiated stop - save state with last_app = None
                    self.stop_current_app(save_state=True)

                elif action == "config":
                    if self.current_app:
                        key = command.get("key")
                        value = command.get("value")
                        self.current_app.update_config(key, value)
                        # Save updated config
                        if self.current_app_name:
                            self.app_configs[self.current_app_name] = (
                                self.current_app.get_config()
                            )
                        self.save_state()

                elif action == "update_app_config":
                    # Update any app's saved config (current or not)
                    app_name = command.get("app")
                    config = command.get("config", {})

                    if app_name in self.available_apps:
                        # Merge with existing config
                        existing_config = self.app_configs.get(app_name, {})
                        existing_config.update(config)
                        self.app_configs[app_name] = existing_config

                        # If this is the current app, apply changes immediately
                        if app_name == self.current_app_name and self.current_app:
                            for key, value in config.items():
                                self.current_app.update_config(key, value)

                            # Emit WebSocket event for current app config change
                            self._emit_current_app()

                        # Save state
                        self.save_state()
                        logger.info(f"Updated config for {app_name}")

                elif action == "settings":
                    # Update global settings
                    if "brightness" in command:
                        brightness = command["brightness"]
                        self.driver.set_brightness(brightness)
                        self.settings["brightness"] = brightness
                        self.save_state()
                        logger.info(f"Updated brightness to {brightness}")

                        # Emit WebSocket event
                        self._emit_settings()

                elif action == "carousel":
                    # Update carousel settings
                    self.carousel_enabled = command.get("enabled", False)
                    self.carousel_apps = command.get("apps", [])
                    self.carousel_index = 0
                    self.carousel_timer = 0
                    self.last_carousel_time = time.time()

                    # If enabling carousel with apps, start the first one
                    if self.carousel_enabled and self.carousel_apps:
                        first_app_config = self.carousel_apps[0]
                        app_name = first_app_config["app"]
                        config = self.get_app_config(app_name)
                        self.start_app(app_name, config)
                        logger.info(
                            f"Started carousel mode with {len(self.carousel_apps)} apps"
                        )
                    elif not self.carousel_enabled:
                        logger.info("Carousel mode disabled")

                    self.save_state()

                    # Emit WebSocket event
                    self._emit_carousel_config()

                elif action == "quit":
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
        3. Handle carousel rotation if enabled
        4. Sleep briefly to prevent CPU spinning
        """
        self.running = True
        logger.info("Application manager started")

        try:
            while self.running:
                # Process any API commands
                self.process_commands()

                # Handle carousel rotation
                if self.carousel_enabled and self.carousel_apps:
                    current_time = time.time()
                    elapsed = current_time - self.last_carousel_time

                    # Get current app duration (in seconds)
                    current_carousel_config = self.carousel_apps[self.carousel_index]
                    duration = current_carousel_config.get("duration", 10)

                    if elapsed >= duration:
                        # Time to switch to next app in carousel
                        self.carousel_index = (self.carousel_index + 1) % len(
                            self.carousel_apps
                        )
                        next_carousel_config = self.carousel_apps[self.carousel_index]
                        next_app = next_carousel_config["app"]
                        config = self.get_app_config(next_app)

                        logger.info(
                            f"Carousel switching to: {next_app} (#{self.carousel_index + 1}/{len(self.carousel_apps)})"
                        )
                        self.start_app(next_app, config)
                        self.last_carousel_time = current_time

                        # Emit carousel status update
                        self._emit_carousel_config()

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
            # Clean shutdown - save config but preserve last_app
            if self.current_app:
                # Save current config before shutdown
                if self.current_app_name:
                    self.app_configs[self.current_app_name] = (
                        self.current_app.get_config()
                    )
                    self.save_state()  # Save state with last_app preserved
                # Clean up app without clearing last_app
                self.stop_current_app(save_state=False)
            logger.info("Application manager stopped")

    def queue_command(self, command: Dict):
        """
        Queue a command for processing.

        Args:
            command: Command dictionary with 'action' key
        """
        self.command_queue.put(command)

    def load_state(self) -> Tuple[Optional[str], Dict[str, Dict]]:
        """
        Load state from disk.

        Returns:
            Tuple of (last_app_name, app_configs_dict)
        """
        if not os.path.exists(self.state_file):
            logger.info(f"No state file found at {self.state_file}, using defaults")
            return None, {}

        try:
            with open(self.state_file, "r") as f:
                state = json.load(f)

            last_app = state.get("last_app")
            app_configs = state.get("app_configs", {})
            settings = state.get("settings", {})

            # Load carousel settings
            carousel_config = state.get("carousel", {})
            self.carousel_enabled = carousel_config.get("enabled", False)
            self.carousel_apps = carousel_config.get("apps", [])
            self.carousel_index = carousel_config.get("index", 0)
            self.last_carousel_time = time.time()

            # Apply settings
            if "brightness" in settings:
                self.driver.set_brightness(settings["brightness"])
                self.settings = settings

            logger.info(
                f"Loaded state: last_app={last_app}, configs for {len(app_configs)} apps, settings={settings}, carousel={self.carousel_enabled}"
            )
            return last_app, app_configs

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse state file: {e}")
            return None, {}
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None, {}

    def save_state(self):
        """
        Save current state to disk.
        """
        try:
            state = {
                "last_app": self.current_app_name,
                "app_configs": self.app_configs,
                "settings": self.settings,
                "carousel": {
                    "enabled": self.carousel_enabled,
                    "apps": self.carousel_apps,
                    "index": self.carousel_index,
                },
            }

            with open(self.state_file, "w") as f:
                json.dump(state, f, indent=2)

            logger.debug(f"Saved state: last_app={self.current_app_name}")

        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def get_app_config(self, app_name: str) -> Dict:
        """
        Get the saved configuration for an app.

        Args:
            app_name: Name of the app

        Returns:
            Configuration dictionary, or empty dict if none saved
        """
        return self.app_configs.get(app_name, {})

    def get_carousel_config(self) -> Dict:
        """
        Get the current carousel configuration.

        Returns:
            Dictionary with carousel settings
        """
        return {
            "enabled": self.carousel_enabled,
            "apps": self.carousel_apps,
            "current_index": self.carousel_index,
        }

    def update_carousel_config(self, enabled: bool, apps: List[Dict]):
        """
        Update carousel configuration.

        Args:
            enabled: Whether carousel mode is enabled
            apps: List of {app: str, duration: int} dictionaries
        """
        self.queue_command(
            {
                "action": "carousel",
                "enabled": enabled,
                "apps": apps,
            }
        )

    def _emit_current_app(self):
        """Emit current app state via WebSocket."""
        if self.socketio:
            try:
                config = self.current_app.get_config() if self.current_app else {}
                self.socketio.emit(
                    "current_app",
                    {"app": self.current_app_name, "config": config},
                    namespace="/",
                )
            except Exception as e:
                logger.debug(f"Failed to emit current_app event: {e}")

    def _emit_settings(self):
        """Emit settings via WebSocket."""
        if self.socketio:
            try:
                self.socketio.emit(
                    "settings",
                    {"brightness": self.driver.get_brightness()},
                    namespace="/",
                )
            except Exception as e:
                logger.debug(f"Failed to emit settings event: {e}")

    def _emit_carousel_config(self):
        """Emit carousel config via WebSocket."""
        if self.socketio:
            try:
                self.socketio.emit(
                    "carousel_config", self.get_carousel_config(), namespace="/"
                )
            except Exception as e:
                logger.debug(f"Failed to emit carousel_config event: {e}")
