#!/bin/bash
# Test all examples to verify imports work

echo "Testing retroboard examples..."
echo "=============================="
echo

echo "1. Testing test_text.py..."
timeout 3 python3 test_text.py 2>&1 | grep -E "(Testing|Font loaded|Test [0-9]|complete)" || echo "FAILED"
echo

echo "2. Testing imports..."
python3 -c "from drivers import create_driver, BDFFont; print('✓ Imports successful')" || echo "FAILED"
echo

echo "3. Testing driver creation..."
python3 -c "
from drivers import create_driver
d = create_driver(use_hardware=False, width=64, height=32)
print(f'✓ Driver created: {d.get_width()}x{d.get_height()}')
" || echo "FAILED"
echo

echo "4. Testing font loading..."
python3 -c "
from drivers import BDFFont
f = BDFFont('./rpi-rgb-led-matrix/fonts/6x10.bdf')
print(f'✓ Font loaded: {len(f.glyphs)} glyphs')
" || echo "FAILED"
echo

echo "5. Testing text rendering..."
python3 -c "
from drivers import create_driver, BDFFont
d = create_driver(use_hardware=False, width=32, height=32)
f = BDFFont('./rpi-rgb-led-matrix/fonts/6x10.bdf')
c = d.create_frame_canvas()
w = f.draw_text(c, 2, 10, 'Test', 255, 255, 255)
print(f'✓ Text rendered: width={w}')
" || echo "FAILED"
echo

echo "=============================="
echo "All tests completed!"
