"""
Matrix Server - Main entry point for the LED matrix application server.

This starts the API server and application manager, allowing remote control
of the LED matrix through HTTP requests.
"""

import argparse
import logging
import threading
from drivers import create_driver
from manager import ApplicationManager
from apps import discover_apps
from api import create_api

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="LED Matrix Application Server")
    parser.add_argument(
        "--hardware",
        action="store_true",
        help="Use hardware driver (default: simulated)",
    )
    parser.add_argument(
        "--rows", type=int, default=32, help="Matrix rows (default: 32)"
    )
    parser.add_argument(
        "--cols", type=int, default=64, help="Matrix columns (default: 64)"
    )
    parser.add_argument(
        "--width", type=int, default=64, help="Simulated display width (default: 64)"
    )
    parser.add_argument(
        "--height", type=int, default=32, help="Simulated display height (default: 32)"
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="API server port (default: 5000)"
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="API server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--app", type=str, default="clock", help="Initial app to run (default: clock)"
    )

    parser.add_argument(
        "--ignore-state", action="store_true", help="Ignore saved state and start fresh"
    )

    args = parser.parse_args()

    # Create the matrix driver
    logger.info(f"Creating {'hardware' if args.hardware else 'simulated'} driver...")
    if args.hardware:
        driver = create_driver(
            use_hardware=True,
            rows=args.rows,
            cols=args.cols,
            hardware_mapping="adafruit-hat",
        )
    else:
        driver = create_driver(use_hardware=False, width=args.width, height=args.height)

    logger.info(f"Display: {driver.get_width()}x{driver.get_height()}")

    # Create the application manager
    manager = ApplicationManager(driver)

    # Load saved state (unless --ignore-state is specified)
    last_app = None
    if not args.ignore_state:
        logger.info("Loading saved state...")
        last_app, saved_configs = manager.load_state()
        manager.app_configs = saved_configs
        if last_app:
            logger.info(f"Found saved state: last_app={last_app}")
        else:
            logger.info("No saved state found, will use defaults")

    # Auto-discover and register all applications
    logger.info("Auto-discovering applications...")
    apps = discover_apps()

    for app_name, app_class in apps.items():
        manager.register_app(app_name, app_class)
        logger.info(f"  Registered: {app_name} ({app_class.__name__})")

    if not apps:
        logger.error("No applications found!")
        return

    # Determine which app to start
    # Priority: 1) saved state (if exists), 2) --app argument, 3) first available
    app_to_start = None
    config_to_use = None

    if not args.ignore_state and last_app and last_app in apps:
        # Use saved state
        app_to_start = last_app
        config_to_use = manager.get_app_config(last_app)
        logger.info(f"Restoring last app: {last_app}")
    elif args.app != "clock" or args.ignore_state:
        # User specified an app via --app, or ignoring state
        if args.app in apps:
            app_to_start = args.app
            config_to_use = manager.get_app_config(args.app)
            logger.info(f"Starting app from command line: {args.app}")
        else:
            logger.warning(f"App '{args.app}' not found")

    # Fallback to first available app if nothing selected yet
    if not app_to_start:
        app_to_start = list(apps.keys())[0]
        config_to_use = manager.get_app_config(app_to_start)
        logger.info(f"Starting first available app: {app_to_start}")

    # Start the selected application
    manager.start_app(app_to_start, config_to_use)

    # Create and start the API server with WebSocket support in a separate thread
    logger.info(f"Starting API server with WebSocket on {args.host}:{args.port}")
    api_app, socketio = create_api(manager)
    api_thread = threading.Thread(
        target=lambda: socketio.run(
            api_app,
            host=args.host,
            port=args.port,
            debug=False,
            allow_unsafe_werkzeug=True,
        ),
        daemon=True,
    )
    api_thread.start()

    logger.info("=" * 60)
    logger.info("Matrix Server is running!")
    logger.info(f"API available at: http://{args.host}:{args.port}")
    logger.info(f"WebSocket available at: ws://{args.host}:{args.port}")
    logger.info(f"Available apps: {', '.join(apps.keys())}")
    logger.info("")
    logger.info("API Endpoints:")
    logger.info("  GET  /api/apps      - List available apps")
    logger.info("  GET  /api/current   - Get current app info")
    logger.info("  POST /api/switch    - Switch to different app")
    logger.info("  POST /api/stop      - Stop current app")
    logger.info("  POST /api/config    - Update app config")
    logger.info("  GET  /api/health    - Health check")
    logger.info("")
    logger.info("WebSocket Events:")
    logger.info("  current_app         - App changes")
    logger.info("  settings            - Settings changes")
    logger.info("  carousel_config     - Carousel updates")
    logger.info("=" * 60)
    logger.info("Press Ctrl+C to stop")
    logger.info("")

    # Run the application manager (blocks until interrupted)
    try:
        manager.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        driver.clear()
        logger.info("Goodbye!")


if __name__ == "__main__":
    main()
