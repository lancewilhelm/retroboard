# Installation Guide

## Prerequisites

- Raspberry Pi (any model with GPIO)
- LED Matrix hardware (optional - can use simulated mode)
- Python 3.7 or higher

## Setup

### 1. Install System Dependencies

The underlying `rpi-rgb-led-matrix` library should already be installed if you have the hardware.

### 2. Set Up Python Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv ~/venvs/matrix

# Activate it
source ~/venvs/matrix/bin/activate
```

### 3. Install Python Dependencies

For the basic drivers and text rendering:
```bash
# No additional dependencies needed!
```

For the Matrix Application Server:
```bash
# Install Flask
pip install flask

# Or use the requirements file
pip install -r requirements.txt
```

## Running Examples

### Basic Examples (No Server)

```bash
# Activate venv if using one
source ~/venvs/matrix/bin/activate

# Run examples (simulated mode)
python3 clock.py
python3 scroll_text.py
python3 stars.py
python3 test_text.py

# With hardware (requires sudo)
sudo ~/venvs/matrix/bin/python3 clock.py
```

### Application Server

```bash
# Activate venv if using one
source ~/venvs/matrix/bin/activate

# Start server (simulated mode)
python3 server.py

# With hardware (requires sudo for GPIO access)
sudo ~/venvs/matrix/bin/python3 server.py --hardware
```

## Verification

Test that everything works:

```bash
# Activate venv
source ~/venvs/matrix/bin/activate

# Test text rendering
python3 test_text.py

# Test server components
python3 -c "
from drivers import create_driver
from apps import ClockApp
from manager import ApplicationManager

driver = create_driver(use_hardware=False, width=32, height=32)
manager = ApplicationManager(driver)
manager.register_app('clock', ClockApp)
print('✅ All components working!')
"
```

## Using with Virtual Environment

If using a virtual environment, you have two options:

### Option 1: Activate the venv (recommended)
```bash
source ~/venvs/matrix/bin/activate
python3 server.py
```

### Option 2: Use the venv Python directly
```bash
~/venvs/matrix/bin/python3 server.py
```

### Option 3: With sudo (for hardware)
```bash
sudo ~/venvs/matrix/bin/python3 server.py --hardware
```

## Troubleshooting

### Flask Not Found
```bash
# Install Flask in your venv
source ~/venvs/matrix/bin/activate
pip install flask
```

### Import Errors
Make sure you're running from the `retroboard` directory:
```bash
cd ~/retroboard
python3 server.py
```

### Permission Denied (Hardware Mode)
Hardware mode requires GPIO access:
```bash
sudo ~/venvs/matrix/bin/python3 server.py --hardware
```

### Module Not Found
Ensure the virtual environment is activated:
```bash
source ~/venvs/matrix/bin/activate
which python3  # Should show /home/pi/venvs/matrix/bin/python3
```

## What Gets Installed

- **No dependencies**: Basic drivers and text rendering
- **Flask**: Only needed for the application server
- **rpi-rgb-led-matrix**: Already installed for hardware support

The project is intentionally lightweight!
