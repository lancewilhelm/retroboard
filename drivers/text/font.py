"""
BDF Font Parser and Renderer

This module implements a simple BDF (Bitmap Distribution Format) font parser
and renderer. BDF is a text-based bitmap font format where each character is
defined as a grid of pixels.

The implementation is intentionally simple and educational, prioritizing
readability over performance.
"""


class Glyph:
    """
    Represents a single character's bitmap data.
    
    A glyph contains:
    - bitmap: List of rows, where each row is a list of booleans (True = pixel on)
    - width: How many pixels wide the character is
    - height: How many pixels tall the character is
    - x_offset: Horizontal adjustment from drawing position
    - y_offset: Vertical adjustment from baseline
    - device_width: How far to advance the cursor after drawing this character
    """
    
    def __init__(self):
        self.bitmap = []        # List of lists: [[bool, bool, ...], [...], ...]
        self.width = 0          # Width of the bitmap
        self.height = 0         # Height of the bitmap
        self.x_offset = 0       # X offset from drawing position
        self.y_offset = 0       # Y offset from baseline
        self.device_width = 0   # How far to move cursor after drawing
    
    def __repr__(self):
        return f"Glyph(width={self.width}, height={self.height}, device_width={self.device_width})"


class BDFFont:
    """
    BDF Font loader and renderer.
    
    Loads a BDF font file and provides methods to draw text on a canvas.
    Works with any canvas that has a set_pixel(x, y, r, g, b) method.
    
    Usage:
        font = BDFFont("path/to/font.bdf")
        font.draw_text(canvas, 10, 20, "Hello!", 255, 255, 255)
    """
    
    def __init__(self, font_path=None):
        """
        Initialize the font.
        
        Args:
            font_path: Optional path to BDF font file to load immediately
        """
        self.glyphs = {}        # Dictionary mapping character code to Glyph
        self.font_height = 0    # Total height of the font
        self.baseline = 0       # Baseline position (pixels from top)
        
        if font_path:
            self.load_font(font_path)
    
    def load_font(self, font_path):
        """
        Load a BDF font file.
        
        Parses the BDF file and stores all character glyphs.
        
        Args:
            font_path: Path to the .bdf font file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(font_path, 'r') as f:
                self._parse_bdf(f)
            return True
        except Exception as e:
            print(f"Error loading font: {e}")
            return False
    
    def _parse_bdf(self, file):
        """
        Parse a BDF font file.
        
        This reads the file line by line and extracts character definitions.
        BDF format is line-based with keywords like ENCODING, BITMAP, etc.
        
        Args:
            file: Open file object
        """
        current_glyph = None
        current_encoding = None
        in_bitmap = False
        bitmap_row = 0
        
        for line in file:
            line = line.strip()
            
            # Parse global font properties
            if line.startswith('FONTBOUNDINGBOX'):
                # FONTBOUNDINGBOX width height xoff yoff
                parts = line.split()
                if len(parts) >= 5:
                    self.font_height = int(parts[2])
                    y_offset = int(parts[4])
                    self.baseline = self.font_height + y_offset
            
            # Start of a new character
            elif line.startswith('ENCODING'):
                # ENCODING <character code>
                parts = line.split()
                if len(parts) >= 2:
                    current_encoding = int(parts[1])
                    current_glyph = Glyph()
            
            # Device width (how far to advance cursor)
            elif line.startswith('DWIDTH') and current_glyph:
                # DWIDTH <x> <y>
                parts = line.split()
                if len(parts) >= 2:
                    current_glyph.device_width = int(parts[1])
            
            # Bounding box for this character
            elif line.startswith('BBX') and current_glyph:
                # BBX <width> <height> <xoff> <yoff>
                parts = line.split()
                if len(parts) >= 5:
                    current_glyph.width = int(parts[1])
                    current_glyph.height = int(parts[2])
                    current_glyph.x_offset = int(parts[3])
                    current_glyph.y_offset = int(parts[4])
                    # Initialize bitmap storage
                    current_glyph.bitmap = []
            
            # Start of bitmap data
            elif line.startswith('BITMAP'):
                in_bitmap = True
                bitmap_row = 0
            
            # End of character definition
            elif line.startswith('ENDCHAR'):
                if current_glyph and current_encoding is not None:
                    # Store the completed glyph
                    self.glyphs[current_encoding] = current_glyph
                current_glyph = None
                current_encoding = None
                in_bitmap = False
            
            # Parse bitmap data
            elif in_bitmap and current_glyph:
                # Each line is a hex string representing one row of pixels
                row_data = self._parse_hex_row(line, current_glyph.width)
                current_glyph.bitmap.append(row_data)
                bitmap_row += 1
    
    def _parse_hex_row(self, hex_string, width):
        """
        Convert a hex string to a list of booleans representing pixels.
        
        BDF stores each row as a hex number. We need to convert it to bits.
        For example: "F0" = 11110000 in binary
        
        Args:
            hex_string: Hex digits representing the row (e.g., "F0", "A8")
            width: Expected width of the character
            
        Returns:
            List of booleans, one per pixel
        """
        # Convert hex string to integer
        try:
            value = int(hex_string, 16)
        except ValueError:
            return [False] * width
        
        # Convert to binary and extract bits
        row = []
        # We need to read bits from left to right (most significant first)
        # Calculate how many bits we need to read
        num_bits = (len(hex_string) * 4)  # Each hex digit = 4 bits
        
        for i in range(num_bits - 1, -1, -1):
            bit = (value >> i) & 1
            row.append(bit == 1)
            if len(row) >= width:
                break
        
        # Pad with False if needed
        while len(row) < width:
            row.append(False)
        
        return row
    
    def draw_text(self, canvas, x, y, text, r, g, b, spacing=0):
        """
        Draw text on a canvas.
        
        The y coordinate represents the baseline of the text.
        
        Args:
            canvas: Canvas object with set_pixel(x, y, r, g, b) method
            x: X coordinate (left edge of first character)
            y: Y coordinate (baseline of text)
            text: String to draw
            r: Red color value (0-255)
            g: Green color value (0-255)
            b: Blue color value (0-255)
            spacing: Extra spacing between characters (default: 0)
            
        Returns:
            Total width of drawn text in pixels
        """
        current_x = x
        
        for char in text:
            # Get the character code
            char_code = ord(char)
            
            # Look up the glyph
            glyph = self.glyphs.get(char_code)
            
            if glyph:
                # Draw this character
                self.draw_glyph(canvas, current_x, y, glyph, r, g, b)
                # Move cursor forward
                current_x += glyph.device_width + spacing
            else:
                # Character not in font, skip it or draw a placeholder
                # For now, just advance by average character width
                current_x += 6 + spacing
        
        return current_x - x
    
    def draw_glyph(self, canvas, x, y, glyph, r, g, b):
        """
        Draw a single character glyph on the canvas.
        
        Args:
            canvas: Canvas object with set_pixel(x, y, r, g, b) method
            x: X coordinate
            y: Y coordinate (baseline)
            glyph: Glyph object to draw
            r: Red color value (0-255)
            g: Green color value (0-255)
            b: Blue color value (0-255)
        """
        # Calculate actual drawing position
        # y is the baseline, we need to offset by glyph position
        draw_y = y - glyph.height - glyph.y_offset
        draw_x = x + glyph.x_offset
        
        # Draw each pixel in the bitmap
        for row_idx, row in enumerate(glyph.bitmap):
            for col_idx, pixel_on in enumerate(row):
                if pixel_on:
                    # Draw the pixel
                    pixel_x = draw_x + col_idx
                    pixel_y = draw_y + row_idx
                    canvas.set_pixel(pixel_x, pixel_y, r, g, b)
    
    def get_text_width(self, text, spacing=0):
        """
        Calculate the width of text without drawing it.
        
        Useful for centering or right-aligning text.
        
        Args:
            text: String to measure
            spacing: Extra spacing between characters
            
        Returns:
            Width in pixels
        """
        width = 0
        for char in text:
            char_code = ord(char)
            glyph = self.glyphs.get(char_code)
            if glyph:
                width += glyph.device_width + spacing
            else:
                width += 6 + spacing  # Default width for missing characters
        
        # Remove trailing spacing
        if spacing and len(text) > 0:
            width -= spacing
            
        return width
    
    def height(self):
        """
        Get the font height.
        
        Returns:
            Font height in pixels
        """
        return self.font_height
