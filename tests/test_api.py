"""
Test script for the Matrix Server API.

This script tests all API endpoints to verify functionality.
"""

import time
import requests
import sys

API_URL = "http://localhost:5000/api"


def test_api():
    """Test all API endpoints."""
    print("=" * 60)
    print("Matrix Server API Test")
    print("=" * 60)
    print()
    print("Make sure the server is running:")
    print("  python3 server.py")
    print()
    input("Press Enter when server is ready...")
    print()
    
    try:
        # Test 1: Health check
        print("1. Testing health endpoint...")
        response = requests.get(f"{API_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()
        
        # Test 2: List apps
        print("2. Listing available apps...")
        response = requests.get(f"{API_URL}/apps")
        data = response.json()
        print(f"   Available apps: {data['apps']}")
        print(f"   Current app: {data['current']}")
        print()
        
        # Test 3: Get current app
        print("3. Getting current app info...")
        response = requests.get(f"{API_URL}/current")
        data = response.json()
        print(f"   App: {data['app']}")
        print(f"   Config: {data['config']}")
        print()
        
        # Test 4: Switch to scroll_text
        print("4. Switching to scroll_text...")
        response = requests.post(f"{API_URL}/switch", json={
            "app": "scroll_text",
            "config": {
                "text": "API Test Running!",
                "color": [255, 0, 0],
                "speed": 2
            }
        })
        print(f"   Response: {response.json()}")
        print("   (You should see scrolling red text)")
        time.sleep(5)
        print()
        
        # Test 5: Update config
        print("5. Updating scroll text color to green...")
        response = requests.post(f"{API_URL}/config", json={
            "color": [0, 255, 0]
        })
        print(f"   Response: {response.json()}")
        print("   (Text should now be green)")
        time.sleep(3)
        print()
        
        # Test 6: Switch to stars
        print("6. Switching to stars...")
        response = requests.post(f"{API_URL}/switch", json={
            "app": "stars",
            "config": {
                "spawn_rate": 3,
                "lifetime": 50
            }
        })
        print(f"   Response: {response.json()}")
        print("   (You should see twinkling stars)")
        time.sleep(5)
        print()
        
        # Test 7: Switch to clock
        print("7. Switching to clock...")
        response = requests.post(f"{API_URL}/switch", json={
            "app": "clock",
            "config": {
                "color": [0, 255, 255]
            }
        })
        print(f"   Response: {response.json()}")
        print("   (You should see the clock)")
        time.sleep(3)
        print()
        
        # Test 8: Stop app
        print("8. Stopping current app...")
        response = requests.post(f"{API_URL}/stop")
        print(f"   Response: {response.json()}")
        print("   (Display should be blank)")
        time.sleep(2)
        print()
        
        # Test 9: Start clock again
        print("9. Starting clock again...")
        response = requests.post(f"{API_URL}/switch", json={
            "app": "clock"
        })
        print(f"   Response: {response.json()}")
        print()
        
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
        print("   Make sure the server is running:")
        print("   python3 server.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    test_api()
