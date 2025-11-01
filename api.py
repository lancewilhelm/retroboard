"""
HTTP API for controlling the LED matrix.

Provides REST endpoints to switch applications and manage the matrix.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

logger = logging.getLogger(__name__)


def create_api(manager):
    """
    Create and configure the Flask API.

    Args:
        manager: ApplicationManager instance

    Returns:
        Flask app instance
    """
    app = Flask(__name__)

    # Enable CORS for web application
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route("/api/apps", methods=["GET"])
    def list_apps():
        """List all available applications."""
        return jsonify(
            {
                "apps": manager.get_available_apps(),
                "current": manager.get_current_app_name(),
            }
        )

    @app.route("/api/current", methods=["GET"])
    def get_current():
        """Get information about the currently running app."""
        current = manager.get_current_app_name()
        if current:
            config = manager.current_app.get_config() if manager.current_app else {}
            return jsonify({"app": current, "config": config})
        else:
            return jsonify({"app": None, "config": {}})

    @app.route("/api/switch", methods=["POST"])
    def switch_app():
        """Switch to a different application."""
        data = request.get_json()

        if not data or "app" not in data:
            return jsonify({"error": "Missing app name"}), 400

        app_name = data["app"]
        config = data.get("config", {})

        # Queue the switch command
        manager.queue_command({"action": "switch", "app": app_name, "config": config})

        return jsonify({"success": True, "app": app_name})

    @app.route("/api/stop", methods=["POST"])
    def stop_app():
        """Stop the currently running application."""
        manager.queue_command({"action": "stop"})

        return jsonify({"success": True})

    @app.route("/api/config", methods=["POST"])
    def update_config():
        """Update configuration of the current app."""
        data = request.get_json()

        if not data:
            return jsonify({"error": "Missing configuration data"}), 400

        # Queue config updates
        for key, value in data.items():
            manager.queue_command({"action": "config", "key": key, "value": value})

        return jsonify({"success": True})

    @app.route("/api/apps/<app_name>/config", methods=["GET"])
    def get_app_config(app_name):
        """Get saved configuration for a specific app."""
        if app_name not in manager.get_available_apps():
            return jsonify({"error": "App not found"}), 404

        config = manager.get_app_config(app_name)
        return jsonify({"app": app_name, "config": config})

    @app.route("/api/apps/<app_name>/config", methods=["POST"])
    def update_app_config(app_name):
        """Update saved configuration for a specific app."""
        if app_name not in manager.get_available_apps():
            return jsonify({"error": "App not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing configuration data"}), 400

        # Queue the update command
        manager.queue_command(
            {"action": "update_app_config", "app": app_name, "config": data}
        )

        return jsonify({"success": True, "app": app_name})

    @app.route("/api/settings", methods=["GET"])
    def get_settings():
        """Get global settings."""
        brightness = manager.driver.get_brightness()
        return jsonify({"brightness": brightness})

    @app.route("/api/settings", methods=["POST"])
    def update_settings():
        """Update global settings."""
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing settings data"}), 400

        # Update brightness if provided
        if "brightness" in data:
            brightness = data["brightness"]
            if not isinstance(brightness, int) or brightness < 0 or brightness > 100:
                return jsonify({"error": "Brightness must be between 0 and 100"}), 400

            # Queue the settings command
            manager.queue_command({"action": "settings", "brightness": brightness})

        return jsonify({"success": True})

    @app.route("/api/carousel", methods=["GET"])
    def get_carousel():
        """Get carousel configuration."""
        return jsonify(manager.get_carousel_config())

    @app.route("/api/carousel", methods=["POST"])
    def update_carousel():
        """Update carousel configuration."""
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing carousel data"}), 400

        enabled = data.get("enabled", False)
        apps = data.get("apps", [])

        # Validate apps list
        if enabled and not apps:
            return jsonify({"error": "Carousel enabled but no apps specified"}), 400

        # Validate each app in the list
        available_apps = manager.get_available_apps()
        for app_config in apps:
            if "app" not in app_config:
                return jsonify({"error": "Each app entry must have 'app' field"}), 400
            if app_config["app"] not in available_apps:
                return (
                    jsonify({"error": f"App not found: {app_config['app']}"}),
                    404,
                )
            if "duration" not in app_config:
                return (
                    jsonify({"error": "Each app entry must have 'duration' field"}),
                    400,
                )
            if (
                not isinstance(app_config["duration"], (int, float))
                or app_config["duration"] <= 0
            ):
                return (
                    jsonify({"error": "Duration must be a positive number"}),
                    400,
                )

        # Update carousel configuration
        manager.update_carousel_config(enabled, apps)

        return jsonify({"success": True, "enabled": enabled, "apps": apps})

    @app.route("/api/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify(
            {
                "status": "ok",
                "manager_running": manager.running,
                "current_app": manager.get_current_app_name(),
            }
        )

    # Disable Flask's default logging for cleaner output
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    return app
