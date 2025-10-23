# Retroboard Project Structure

This document describes the organization of the retroboard project.

## Directory Layout

```
retroboard/
├── drivers/                      # Core driver package
│   ├── __init__.py               # Package exports (create_driver, BDFFont, etc.)
│   ├── matrix.py                 # Matrix driver implementation
│   │                             # - Canvas (abstract base class)
│   │                             # - MatrixDriver (abstract driver class)
│   │                             # - HardwareDriver (real LED matrix)
│   │                             # - SimulatedDriver (in-memory simulation)
│   │                             # - create_driver() factory function
│   └── text/                     # Text rendering subpackage
│       ├── __init__.py           # Exports BDFFont
│       └── font.py               # BDF font parser and renderer
│
├── examples/                     # Example applications
│   ├── example_driver.py         # Basic driver features demo
│   └── example_double_buffer.py  # Double-buffering animations
│
├── tests/                        # Test suite
│   └── test_driver.py            # Driver unit tests
│
├── rpi-rgb-led-matrix/           # Underlying C++ library
│   ├── fonts/                    # BDF font files
│   ├── include/                  # C++ headers
│   ├── lib/                      # Compiled libraries
│   └── bindings/python/          # Python bindings
│
├── clock.py                      # Digital clock demo
├── scroll_text.py                # Scrolling text demo
├── test_text.py                  # Text rendering tests
├── stars.py                      # Stars animation demo
│
├── README.md                     # Main documentation
├── QUICKSTART.md                 # Quick start guide
├── TEXT_RENDERING.md             # Text rendering deep dive
├── DRIVER_IMPLEMENTATION.md      # Driver technical details
└── STRUCTURE.md                  # This file
```

## Import Patterns

### Standard Usage

```python
from drivers import create_driver, BDFFont

# Create a driver
driver = create_driver(use_hardware=False, width=64, height=32)

# Load a font
font = BDFFont("./rpi-rgb-led-matrix/fonts/6x10.bdf")

# Use them together
canvas = driver.create_frame_canvas()
font.draw_text(canvas, 10, 20, "Hello!", 255, 255, 255)
canvas = driver.update(canvas)
```

### Advanced Usage

```python
from drivers import HardwareDriver, SimulatedDriver, Canvas, MatrixDriver

# Direct instantiation for more control
hardware = HardwareDriver(rows=64, cols=64, hardware_mapping="adafruit-hat")
simulator = SimulatedDriver(width=128, height=64)

# Type hints for functions
def draw_something(canvas: Canvas):
    canvas.set_pixel(10, 10, 255, 0, 0)
```

## Module Responsibilities

### `drivers/matrix.py`

**Purpose**: Provides abstraction over LED matrix hardware

**Exports**:
- `Canvas` - Abstract base class for drawable surfaces
- `MatrixDriver` - Abstract driver with double-buffering support
- `HardwareDriver` - Real hardware implementation
- `SimulatedDriver` - In-memory simulation
- `create_driver()` - Factory function for easy driver creation

**Key Features**:
- Unified interface for hardware and simulation
- Double-buffering support
- Brightness control
- Pixel-level drawing operations

### `drivers/text/font.py`

**Purpose**: BDF font parsing and text rendering

**Exports**:
- `BDFFont` - Font loader and text renderer
- `Glyph` - Character bitmap representation

**Key Features**:
- Parse BDF bitmap font files
- Render text on any Canvas-compatible surface
- Calculate text dimensions
- Support for character spacing
- Works with both hardware and simulated drivers

### `drivers/__init__.py`

**Purpose**: Package entry point with convenient exports

**Exports everything you need**:
```python
from drivers import (
    Canvas,           # For type hints
    MatrixDriver,     # For type hints
    HardwareDriver,   # Direct instantiation
    SimulatedDriver,  # Direct instantiation
    create_driver,    # Easy driver creation
    BDFFont          # Text rendering
)
```

## Design Principles

### 1. Single Package for Related Functionality
All driver-related code lives in the `drivers/` package:
- Matrix control
- Text rendering
- Hardware abstraction

### 2. Clean Imports
Users can import everything from one place:
```python
from drivers import create_driver, BDFFont  # Simple!
```

### 3. Clear Separation
- **drivers/matrix.py**: Hardware abstraction
- **drivers/text/**: Text rendering (separate concern)
- **examples/**: Usage demonstrations
- **tests/**: Verification code

### 4. Flexible Usage
Support multiple usage patterns:
- Factory function for simplicity: `create_driver()`
- Direct instantiation for control: `HardwareDriver()`, `SimulatedDriver()`
- Abstract interfaces for extensibility: `Canvas`, `MatrixDriver`

## Adding New Features

### Adding to Matrix Driver

Edit `drivers/matrix.py`:
1. Add method to `Canvas` abstract class
2. Implement in `HardwareDriver`
3. Implement in `SimulatedDriver`
4. Export from `drivers/__init__.py` if needed

### Adding Text Effects

Edit `drivers/text/font.py`:
1. Add method to `BDFFont` class
2. Use existing `draw_glyph()` as foundation
3. Test with `test_text.py`

### Adding New Drivers

Create `drivers/new_driver.py`:
1. Inherit from `MatrixDriver`
2. Implement all abstract methods
3. Export from `drivers/__init__.py`
4. Update `create_driver()` if needed

## Migration from Old Structure

If you have old code using `from driver import`, update to:

```python
# Old
from driver import create_driver
from text import BDFFont

# New
from drivers import create_driver, BDFFont
```

All functionality remains the same, just the import path changed.

## Benefits of This Structure

1. **Clarity**: Related code is grouped together
2. **Discoverability**: One package to import from
3. **Maintainability**: Clear module boundaries
4. **Extensibility**: Easy to add new drivers or features
5. **Type Safety**: Clean interfaces for type hints
6. **Testing**: Clear separation aids testing

## File Count Summary

- **Core Driver Files**: 4 (matrix.py, font.py, 2x __init__.py)
- **Example Files**: 6 (clock, scroll, stars, test_text, 2x examples/)
- **Documentation**: 5 (README, QUICKSTART, TEXT_RENDERING, DRIVER_IMPLEMENTATION, STRUCTURE)
- **Tests**: 1 (test_driver.py)

Total project is ~1500 lines of well-documented, organized code.
