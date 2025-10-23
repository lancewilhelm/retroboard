#!/usr/bin/env python3
"""
Quick test to verify Ctrl+C preserves last_app
"""
import json
import os

STATE_FILE = "state.json"

print("Test: Verifying Ctrl+C behavior")
print("=" * 60)

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    print(f"State file exists:")
    print(f"  last_app: {state.get('last_app')}")
    print(f"  app_configs: {list(state.get('app_configs', {}).keys())}")
    
    if state.get('last_app'):
        print(f"\n✓ GOOD: last_app is preserved ({state.get('last_app')})")
    else:
        print(f"\n✗ BAD: last_app is None (should be preserved on Ctrl+C)")
else:
    print("No state file found")
