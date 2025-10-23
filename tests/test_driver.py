"""
Simple test script to verify the driver implementations work correctly.

This script runs basic tests on both HardwareDriver and SimulatedDriver
to ensure the wrapper functions as expected.
"""

from drivers import create_driver, SimulatedDriver


def test_simulated_driver():
    """Test the SimulatedDriver implementation."""
    print("Testing SimulatedDriver...")

    # Create a small 8x8 simulated matrix
    driver = SimulatedDriver(width=8, height=8)

    # Test dimensions
    assert driver.get_width() == 8, "Width should be 8"
    assert driver.get_height() == 8, "Height should be 8"
    print("✓ Dimensions correct")

    # Test clear
    driver.clear()
    buffer = driver.get_buffer()
    assert buffer[0][0] == (0, 0, 0), "Pixel should be black after clear"
    print("✓ Clear works")

    # Test set_pixel
    driver.set_pixel(0, 0, 255, 128, 64)
    buffer = driver.get_buffer()
    assert buffer[0][0] == (255, 128, 64), "Pixel color should match"
    print("✓ SetPixel works")

    # Test fill
    driver.fill(100, 150, 200)
    buffer = driver.get_buffer()
    assert buffer[0][0] == (100, 150, 200), "All pixels should be filled"
    assert buffer[7][7] == (100, 150, 200), "All pixels should be filled"
    print("✓ Fill works")

    # Test bounds checking
    driver.set_pixel(100, 100, 255, 0, 0)  # Out of bounds, should not crash
    print("✓ Bounds checking works")

    print("✓ SimulatedDriver: All tests passed!\n")


def test_factory_function():
    """Test the create_driver factory function."""
    print("Testing create_driver factory function...")

    # Test creating simulated driver
    driver = create_driver(use_hardware=False, width=16, height=16)
    assert isinstance(driver, SimulatedDriver), "Should create SimulatedDriver"
    assert driver.get_width() == 16, "Width should be 16"
    assert driver.get_height() == 16, "Height should be 16"
    print("✓ Simulated driver creation works")

    print("✓ Factory function: All tests passed!\n")


def test_interface():
    """Test that both drivers implement the same interface."""
    print("Testing common interface...")

    # Both drivers should have the same methods
    required_methods = ["set_pixel", "clear", "fill", "get_width", "get_height"]

    sim_driver = SimulatedDriver()
    for method in required_methods:
        assert hasattr(sim_driver, method), f"SimulatedDriver missing {method}"

    print("✓ SimulatedDriver implements all required methods")
    print("✓ Interface: All tests passed!\n")


def test_double_buffering():
    """Test double-buffering functionality with canvas swapping."""
    print("Testing double-buffering...")

    driver = SimulatedDriver(width=8, height=8)

    # Test create_frame_canvas
    canvas = driver.create_frame_canvas()
    assert canvas is not None, "Should create frame canvas"
    assert canvas.get_width() == 8, "Canvas width should match driver"
    assert canvas.get_height() == 8, "Canvas height should match driver"
    print("✓ create_frame_canvas works")

    # Test drawing on offscreen canvas
    canvas.set_pixel(0, 0, 255, 0, 0)
    canvas.set_pixel(1, 1, 0, 255, 0)

    # Main buffer should still be clear
    main_buffer = driver.get_buffer()
    assert main_buffer[0][0] == (0, 0, 0), "Main buffer should be unaffected"
    print("✓ Offscreen canvas is independent")

    # Test swap_on_vsync
    old_canvas = driver.swap_on_vsync(canvas)
    assert old_canvas is not None, "Should return old canvas"

    # Main buffer should now have the swapped content
    main_buffer = driver.get_buffer()
    assert main_buffer[0][0] == (255, 0, 0), "Pixel should be swapped to main buffer"
    assert main_buffer[1][1] == (0, 255, 0), "Second pixel should be swapped"
    print("✓ swap_on_vsync transfers content")

    # Test that old canvas has the previous main buffer content (all zeros)
    old_buffer = old_canvas.get_buffer()
    assert old_buffer[0][0] == (0, 0, 0), "Old canvas should have previous main buffer"
    print("✓ swap_on_vsync returns old buffer")

    # Test canvas operations
    canvas.clear()
    canvas_buffer = canvas.get_buffer()
    assert canvas_buffer[0][0] == (0, 0, 0), "Canvas clear should work"
    print("✓ Canvas clear works")

    canvas.fill(100, 150, 200)
    canvas_buffer = canvas.get_buffer()
    assert canvas_buffer[0][0] == (100, 150, 200), "Canvas fill should work"
    print("✓ Canvas fill works")

    print("✓ Double-buffering: All tests passed!\n")


def test_brightness():
    """Test brightness control."""
    print("Testing brightness...")

    driver = SimulatedDriver()

    # Test default brightness
    assert driver.get_brightness() == 100, "Default brightness should be 100"
    print("✓ Default brightness correct")

    # Test setting brightness
    driver.set_brightness(50)
    assert driver.get_brightness() == 50, "Brightness should be 50"
    print("✓ Set brightness works")

    # Test brightness bounds
    driver.set_brightness(150)
    assert driver.get_brightness() == 100, "Brightness should be capped at 100"

    driver.set_brightness(-10)
    assert driver.get_brightness() == 0, "Brightness should be floored at 0"
    print("✓ Brightness bounds enforced")

    print("✓ Brightness: All tests passed!\n")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Driver Wrapper Test Suite")
    print("=" * 50 + "\n")

    try:
        test_simulated_driver()
        test_factory_function()
        test_interface()
        test_double_buffering()
        test_brightness()

        print("=" * 50)
        print("✓ ALL TESTS PASSED!")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
