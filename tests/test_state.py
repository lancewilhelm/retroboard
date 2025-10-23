#!/usr/bin/env python3
"""
Test script for state persistence.

This script tests that state is properly saved and loaded.
"""

import os
import json
import sys
import time
import requests
from pathlib import Path

STATE_FILE = "state.json"
API_BASE = "http://localhost:5000/api"


def cleanup_state():
    """Remove state file if it exists."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print(f"✓ Cleaned up {STATE_FILE}")


def check_state_file_exists():
    """Check if state file exists."""
    if os.path.exists(STATE_FILE):
        print(f"✓ State file exists: {STATE_FILE}")
        return True
    else:
        print(f"✗ State file not found: {STATE_FILE}")
        return False


def read_state():
    """Read and display state file."""
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        print(f"✓ State file contents:")
        print(json.dumps(state, indent=2))
        return state
    except Exception as e:
        print(f"✗ Failed to read state: {e}")
        return None


def wait_for_server(timeout=10):
    """Wait for server to be ready."""
    print("Waiting for server to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{API_BASE}/health", timeout=1)
            if response.ok:
                print("✓ Server is ready")
                return True
        except:
            time.sleep(0.5)
    print("✗ Server not ready after timeout")
    return False


def get_current_app():
    """Get current running app."""
    try:
        response = requests.get(f"{API_BASE}/current")
        if response.ok:
            data = response.json()
            app = data.get("app")
            config = data.get("config", {})
            print(f"✓ Current app: {app}")
            print(f"  Config: {json.dumps(config, indent=2)}")
            return app, config
        else:
            print(f"✗ Failed to get current app: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"✗ Error getting current app: {e}")
        return None, None


def switch_app(app_name, config=None):
    """Switch to an app."""
    try:
        payload = {"app": app_name}
        if config:
            payload["config"] = config
        response = requests.post(f"{API_BASE}/switch", json=payload)
        if response.ok:
            print(f"✓ Switched to {app_name}")
            if config:
                print(f"  Config: {json.dumps(config, indent=2)}")
            return True
        else:
            print(f"✗ Failed to switch app: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error switching app: {e}")
        return False


def update_config(config):
    """Update current app config."""
    try:
        response = requests.post(f"{API_BASE}/config", json=config)
        if response.ok:
            print(f"✓ Updated config")
            print(f"  Config: {json.dumps(config, indent=2)}")
            return True
        else:
            print(f"✗ Failed to update config: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error updating config: {e}")
        return False


def test_basic_state():
    """Test basic state persistence."""
    print("\n" + "=" * 60)
    print("TEST: Basic State Persistence")
    print("=" * 60)

    # 1. Clean state
    print("\n1. Starting with clean state...")
    cleanup_state()

    print("\n2. Waiting for server (should start with default app)...")
    if not wait_for_server():
        print("✗ TEST FAILED: Server not ready")
        return False

    time.sleep(2)  # Give server time to initialize

    # 3. Check initial app
    print("\n3. Checking initial app...")
    initial_app, initial_config = get_current_app()
    if not initial_app:
        print("✗ TEST FAILED: No app running")
        return False

    # 4. Switch to scroll_text with custom config
    print("\n4. Switching to scroll_text with custom config...")
    custom_config = {
        "text": "State Test Message",
        "color": [255, 100, 50],
        "speed": 3,
    }
    if not switch_app("scroll_text", custom_config):
        print("✗ TEST FAILED: Could not switch app")
        return False

    time.sleep(2)  # Wait for state save

    # 5. Check state file was created
    print("\n5. Checking state file was created...")
    if not check_state_file_exists():
        print("✗ TEST FAILED: State file not created")
        return False

    # 6. Read and verify state
    print("\n6. Verifying state file contents...")
    state = read_state()
    if not state:
        print("✗ TEST FAILED: Could not read state")
        return False

    if state.get("last_app") != "scroll_text":
        print(
            f"✗ TEST FAILED: Expected last_app='scroll_text', got '{state.get('last_app')}'"
        )
        return False

    scroll_config = state.get("app_configs", {}).get("scroll_text", {})
    if scroll_config.get("text") != "State Test Message":
        print(f"✗ TEST FAILED: Config not saved correctly")
        return False

    print("✓ State file contents are correct!")

    print("\n" + "=" * 60)
    print("✓ TEST PASSED: Basic State Persistence")
    print("=" * 60)
    return True


def test_per_app_memory():
    """Test per-app config memory."""
    print("\n" + "=" * 60)
    print("TEST: Per-App Config Memory")
    print("=" * 60)

    print("\n1. Configuring clock with red color...")
    if not switch_app("clock", {"color": [255, 0, 0]}):
        print("✗ TEST FAILED: Could not configure clock")
        return False

    time.sleep(1)

    print("\n2. Switching to stars...")
    if not switch_app("stars", {"spawn_rate": 5}):
        print("✗ TEST FAILED: Could not switch to stars")
        return False

    time.sleep(1)

    print("\n3. Switching back to clock...")
    if not switch_app("clock"):
        print("✗ TEST FAILED: Could not switch back to clock")
        return False

    time.sleep(1)

    print("\n4. Checking if clock still has red color...")
    _, clock_config = get_current_app()
    if clock_config and clock_config.get("color") == [255, 0, 0]:
        print("✓ Clock remembered its red color!")
    else:
        print(f"✗ TEST FAILED: Clock color not preserved: {clock_config}")
        return False

    print("\n" + "=" * 60)
    print("✓ TEST PASSED: Per-App Config Memory")
    print("=" * 60)
    return True


def test_config_update():
    """Test config update persistence."""
    print("\n" + "=" * 60)
    print("TEST: Config Update Persistence")
    print("=" * 60)

    print("\n1. Starting scroll_text...")
    if not switch_app("scroll_text", {"text": "Original Text", "speed": 1}):
        print("✗ TEST FAILED: Could not start scroll_text")
        return False

    time.sleep(1)

    print("\n2. Updating text via config endpoint...")
    if not update_config({"text": "Updated Text", "speed": 5}):
        print("✗ TEST FAILED: Could not update config")
        return False

    time.sleep(1)

    print("\n3. Checking state file...")
    state = read_state()
    if not state:
        print("✗ TEST FAILED: Could not read state")
        return False

    scroll_config = state.get("app_configs", {}).get("scroll_text", {})
    if scroll_config.get("text") == "Updated Text" and scroll_config.get("speed") == 5:
        print("✓ Config update was persisted!")
    else:
        print(f"✗ TEST FAILED: Config not updated in state: {scroll_config}")
        return False

    print("\n" + "=" * 60)
    print("✓ TEST PASSED: Config Update Persistence")
    print("=" * 60)
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("STATE PERSISTENCE TEST SUITE")
    print("=" * 60)
    print("\nNOTE: This test requires the server to be running!")
    print("Start the server with: python3 main.py")
    print("")

    input("Press Enter to start tests (Ctrl+C to cancel)...")

    results = []

    # Run tests
    results.append(("Basic State Persistence", test_basic_state()))
    results.append(("Per-App Config Memory", test_per_app_memory()))
    results.append(("Config Update Persistence", test_config_update()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    failed = 0
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1

    print("")
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 60)

    if failed > 0:
        print("\n✗ SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("\n✓ ALL TESTS PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
