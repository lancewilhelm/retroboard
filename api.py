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
