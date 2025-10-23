# Text Rendering Implementation Guide

This document explains how the custom BDF font parser and text renderer work.

## What is BDF?

BDF (Bitmap Distribution Format) is a simple text-based format for bitmap fonts. Each character is defined as a grid of pixels stored as hex values.

## BDF File Format

### Example Character Definition

```
STARTCHAR exclam          ← Character name
ENCODING 33               ← ASCII/Unicode code (33 = '!')
DWIDTH 6 0                ← Device width: how far to move cursor
BBX 6 10 0 -2             ← Bounding box: width, height, x_offset, y_offset
BITMAP                    ← Start of bitmap data
00                        ← Row 1: 00000000 (all pixels off)
20                        ← Row 2: 00100000 (pixel 2 on)
20                        ← Row 3: 00100000
20                        ← Row 4: 00100000
20                        ← Row 5: 00100000
20                        ← Row 6: 00100000
00                        ← Row 7: 00000000
20                        ← Row 8: 00100000 (the dot)
00                        ← Row 9: 00000000
00                        ← Row 10: 00000000
ENDCHAR                   ← End of character
```

### Hex to Binary

Each hex digit represents 4 bits:
- `0` = `0000`
- `2` = `0010`
- `0` = `0000`
- Result: `00100000` (one pixel on at position 2)

More examples:
- `F0` = `11110000` (4 pixels on)
- `FF` = `11111111` (8 pixels on)
- `A8` = `10101000` (alternating pixels)

## How Our Implementation Works

### 1. Data Structures

```python
class Glyph:
    """Represents one character."""
    bitmap = []           # List of rows: [[True, False, ...], ...]
    width = 0             # Width of bitmap
    height = 0            # Height of bitmap
    x_offset = 0          # Horizontal adjustment
    y_offset = 0          # Vertical adjustment from baseline
    device_width = 0      # How far to advance cursor

class BDFFont:
    """Font loader and renderer."""
    glyphs = {}           # Dict: character_code -> Glyph
    font_height = 0       # Total font height
    baseline = 0          # Baseline position
```

### 2. Loading Process

```python
def load_font(font_path):
    1. Open the BDF file
    2. Parse FONTBOUNDINGBOX to get font height and baseline
    3. For each character:
       a. Read ENCODING to get character code
       b. Read DWIDTH to get cursor advance
       c. Read BBX to get bounding box
       d. Read BITMAP lines and convert hex to bits
       e. Store in glyphs dictionary
```

### 3. Hex Row Parsing

```python
def _parse_hex_row(hex_string, width):
    """Convert hex string like 'F0' to [True, True, True, True, False, ...]"""
    
    # Example: hex_string = "F0", width = 6
    value = int("F0", 16)  # = 240 in decimal
    
    # Convert to binary (most significant bit first)
    # 240 = 11110000 in binary
    # Read left to right: [True, True, True, True, False, False, False, False]
    # Take first 'width' bits: [True, True, True, True, False, False]
    
    return [bit_is_set, bit_is_set, ...]
```

### 4. Drawing Text

```python
def draw_text(canvas, x, y, text, r, g, b):
    current_x = x
    
    for char in text:
        # Look up the glyph
        glyph = glyphs[ord(char)]
        
        # Draw it
        draw_glyph(canvas, current_x, y, glyph, r, g, b)
        
        # Move cursor
        current_x += glyph.device_width
```

### 5. Drawing a Glyph

```python
def draw_glyph(canvas, x, y, glyph, r, g, b):
    # y is the baseline, adjust for glyph position
    draw_y = y - glyph.height - glyph.y_offset
    draw_x = x + glyph.x_offset
    
    # Draw each pixel
    for row_idx, row in enumerate(glyph.bitmap):
        for col_idx, pixel_on in enumerate(row):
            if pixel_on:
                canvas.set_pixel(
                    draw_x + col_idx,
                    draw_y + row_idx,
                    r, g, b
                )
```

## Visual Example

Drawing the letter "I" at position (10, 20):

```
Font definition:
ENCODING 73  (letter 'I')
DWIDTH 6 0
BBX 6 10 0 -2
BITMAP
00   = 000000
70   = 011100
20   = 001000
20   = 001000
20   = 001000
20   = 001000
70   = 011100
00   = 000000
00   = 000000
00   = 000000

Result on canvas:
   x: 10 11 12 13 14 15
y:10    [   ] [   ] [   ]
  11    [ █ ] [ █ ] [ █ ]
  12    [   ] [ █ ] [   ]
  13    [   ] [ █ ] [   ]
  14    [   ] [ █ ] [   ]
  15    [   ] [ █ ] [   ]
  16    [ █ ] [ █ ] [ █ ]
  17    [   ] [   ] [   ]
  18    [   ] [   ] [   ]
  19    [   ] [   ] [   ]

Cursor advances by 6 pixels for next character.
```

## Baseline Explanation

The baseline is where most letters "sit". Letters like 'y' and 'g' extend below it (descenders).

```
        ← Top of font (y_offset from baseline)
Hello!  ← Most letters sit here (baseline)
    y   ← Descenders go below
```

When you call `draw_text(canvas, x, y, "Hello!", ...)`:
- `y` is the baseline position
- The code calculates where to actually draw using offsets
- This makes text alignment natural

## Why This Works

1. **Universal Interface**: Uses `canvas.set_pixel()` which every driver implements
2. **No Dependencies**: Pure Python, no C++ libraries needed
3. **Portable**: Works on hardware and simulation
4. **Simple**: Easy to understand and modify
5. **Extensible**: Can add effects, colors, animations easily

## Performance Notes

For small displays (64x32), Python is fast enough. The bottleneck is usually the display update, not the text rendering.

Typical performance:
- Loading a font: ~10-50ms (one-time cost)
- Drawing 8 characters: <1ms
- This is 1000x faster than the 16.6ms needed for 60fps

## Extending the Library

Easy additions you can make:

### 1. Background Color
```python
def draw_text_with_bg(canvas, x, y, text, fg_color, bg_color):
    # Draw background rectangle first
    width = get_text_width(text)
    for py in range(y - font_height, y):
        for px in range(x, x + width):
            canvas.set_pixel(px, py, bg_color[0], bg_color[1], bg_color[2])
    # Then draw text on top
    draw_text(canvas, x, y, text, fg_color[0], fg_color[1], fg_color[2])
```

### 2. Scrolling Text
```python
offset = 0
while True:
    canvas.clear()
    font.draw_text(canvas, 64 - offset, 16, "Scrolling!", 255, 255, 255)
    offset = (offset + 1) % (64 + text_width)
    canvas = driver.update(canvas)
```

### 3. Gradient Text
```python
text = "GRADIENT"
for i, char in enumerate(text):
    r = int(255 * i / len(text))
    g = int(255 * (1 - i / len(text)))
    x += font.draw_text(canvas, x, y, char, r, g, 0)
```

## Comparison with C++ Library

| Feature | C++ Library | Our Library |
|---------|------------|-------------|
| Works with hardware | ✅ Yes | ✅ Yes |
| Works with simulation | ❌ No | ✅ Yes |
| Performance | Very fast | Fast enough |
| Easy to modify | ❌ No | ✅ Yes |
| Requires compilation | ✅ Yes | ❌ No |
| UTF-8 support | ✅ Full | Basic (ASCII) |
| Outline fonts | ✅ Yes | ❌ No (yet) |

## Summary

The text rendering library:
1. Parses human-readable BDF font files
2. Stores character bitmaps in simple data structures
3. Renders text by calling `set_pixel()` for each "on" pixel
4. Works with any canvas that implements the Canvas interface
5. Is simple, educational, and easy to extend

This gives you full control over text rendering while keeping the code understandable and maintainable.
