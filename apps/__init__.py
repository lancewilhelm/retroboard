"""
Matrix applications package with auto-discovery.

This package automatically discovers and loads all applications in subdirectories.
To create a new app, simply create a folder with your app class and it will be
automatically discovered and registered.
"""

import os
import sys
import importlib
import inspect
from .base import MatrixApplication

# Export the base class
__all__ = ["MatrixApplication", "discover_apps", "get_app_class"]

# Storage for discovered apps
_discovered_apps = {}


def discover_apps():
    """
    Automatically discover all matrix applications.

    Scans the apps directory for subdirectories and imports any MatrixApplication
    subclasses found. Apps are registered using their folder name.

    Returns:
        Dictionary mapping app names to app classes
    """
    global _discovered_apps

    if _discovered_apps:
        # Already discovered
        return _discovered_apps

    apps_dir = os.path.dirname(__file__)

    # Scan for app directories
    for item in os.listdir(apps_dir):
        item_path = os.path.join(apps_dir, item)

        # Skip non-directories and private folders
        if not os.path.isdir(item_path) or item.startswith("_"):
            continue

        try:
            # Import the app module
            module_name = f"apps.{item}"
            module = importlib.import_module(module_name)

            # Look for MatrixApplication subclasses
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it's a subclass of MatrixApplication (but not the base class itself)
                if issubclass(obj, MatrixApplication) and obj is not MatrixApplication:
                    # Register using folder name
                    _discovered_apps[item] = obj
                    break  # Only take the first app class from each module

        except Exception as e:
            # Skip modules that fail to import
            print(f"Warning: Could not load app '{item}': {e}", file=sys.stderr)
            continue

    return _discovered_apps


def get_app_class(name):
    """
    Get an app class by name.

    Args:
        name: Name of the app (folder name)

    Returns:
        App class or None if not found
    """
    if not _discovered_apps:
        discover_apps()

    return _discovered_apps.get(name)


def get_available_apps():
    """
    Get list of available app names.

    Returns:
        List of app names
    """
    if not _discovered_apps:
        discover_apps()

    return list(_discovered_apps.keys())


# Auto-discover on import
discover_apps()
