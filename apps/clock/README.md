# Clock App

Digital clock that displays the current time in HH:MM:SS format.

## Usage

```bash
# Via API
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "clock"}'
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `font` | string | `6x10` | BDF font title |
| `color` | [r, g, b] | `[255, 255, 255]` | Text color (white) |

## Examples

**Green clock:**
```json
{
  "app": "clock",
  "config": {
    "color": [0, 255, 0]
  }
}
```

**Large font clock:**
```json
{
  "app": "clock",
  "config": {
    "font": "9x18",
    "color": [255, 255, 0]
  }
}
```

**Update color while running:**
```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"color": [255, 0, 0]}'
```

## How It Works

- Checks the time every 100ms
- Only redraws when the second changes
- Text is automatically centered on the display
- Uses baseline positioning for proper text alignment
