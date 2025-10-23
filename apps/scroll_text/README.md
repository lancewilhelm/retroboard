# Scroll Text App

Displays scrolling text that moves from right to left across the display.

## Usage

```bash
# Via API
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "scroll_text", "config": {"text": "Hello World!"}}'
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `text` | string | `"Hello, World!"` | Text to display |
| `font` | string | `6x10` | BDF font title |
| `color` | [r, g, b] | `[0, 255, 255]` | Text color |
| `speed` | number | `1` | Scroll speed in pixels per frame |
| `fps` | number | `30` | Frames per second |

## Examples

**Fast red scrolling text:**
```json
{
  "app": "scroll_text",
  "config": {
    "text": "Breaking News!",
    "color": [255, 0, 0],
    "speed": 3
  }
}
```

**Slow ticker:**
```json
{
  "app": "scroll_text",
  "config": {
    "text": "Stock prices: AAPL $150, GOOGL $140",
    "speed": 1,
    "fps": 20,
    "color": [0, 255, 0]
  }
}
```

**Update text while running:**
```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"text": "Updated message!"}'
```

## How It Works

- Text starts off-screen to the right
- Moves left by `speed` pixels each frame
- When text completely scrolls off the left, it resets to the right
- Text is vertically centered automatically
