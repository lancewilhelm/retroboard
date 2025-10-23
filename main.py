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
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='LED Matrix Application Server')
    parser.add_argument('--hardware', action='store_true', 
                       help='Use hardware driver (default: simulated)')
    parser.add_argument('--rows', type=int, default=32,
                       help='Matrix rows (default: 32)')
    parser.add_argument('--cols', type=int, default=64,
                       help='Matrix columns (default: 64)')
    parser.add_argument('--width', type=int, default=64,
                       help='Simulated display width (default: 64)')
    parser.add_argument('--height', type=int, default=32,
                       help='Simulated display height (default: 32)')
    parser.add_argument('--port', type=int, default=5000,
                       help='API server port (default: 5000)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='API server host (default: 0.0.0.0)')
    parser.add_argument('--app', type=str, default='clock',
                       help='Initial app to run (default: clock)')
    
    args = parser.parse_args()
    
    # Create the matrix driver
    logger.info(f"Creating {'hardware' if args.hardware else 'simulated'} driver...")
    if args.hardware:
        driver = create_driver(
            use_hardware=True,
            rows=args.rows,
            cols=args.cols,
            hardware_mapping="adafruit-hat"
        )
    else:
        driver = create_driver(
            use_hardware=False,
            width=args.width,
            height=args.height
        )
    
    logger.info(f"Display: {driver.get_width()}x{driver.get_height()}")
    
    # Create the application manager
    manager = ApplicationManager(driver)
    
    # Auto-discover and register all applications
    logger.info("Auto-discovering applications...")
    apps = discover_apps()
    
    for app_name, app_class in apps.items():
        manager.register_app(app_name, app_class)
        logger.info(f"  Registered: {app_name} ({app_class.__name__})")
    
    if not apps:
        logger.error("No applications found!")
        return
    
    # Start initial application
    if args.app in apps:
        logger.info(f"Starting initial app: {args.app}")
        manager.start_app(args.app)
    else:
        logger.warning(f"App '{args.app}' not found, starting first available app")
        first_app = list(apps.keys())[0]
        manager.start_app(first_app)
    
    # Create and start the API server in a separate thread
    logger.info(f"Starting API server on {args.host}:{args.port}")
    api_app = create_api(manager)
    api_thread = threading.Thread(
        target=lambda: api_app.run(host=args.host, port=args.port, debug=False),
        daemon=True
    )
    api_thread.start()
    
    logger.info("=" * 60)
    logger.info("Matrix Server is running!")
    logger.info(f"API available at: http://{args.host}:{args.port}")
    logger.info(f"Available apps: {', '.join(apps.keys())}")
    logger.info("")
    logger.info("API Endpoints:")
    logger.info("  GET  /api/apps      - List available apps")
    logger.info("  GET  /api/current   - Get current app info")
    logger.info("  POST /api/switch    - Switch to different app")
    logger.info("  POST /api/stop      - Stop current app")
    logger.info("  POST /api/config    - Update app config")
    logger.info("  GET  /api/health    - Health check")
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


if __name__ == '__main__':
    main()
