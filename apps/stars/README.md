# Stars App

Twinkling colored stars animation with smooth fade in/out effect.

## Usage

```bash
# Via API
curl -X POST http://localhost:5000/api/switch \
  -H "Content-Type: application/json" \
  -d '{"app": "stars"}'
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `spawn_rate` | number | `1` | Number of stars spawned per frame |
| `lifetime` | number | `40` | How many frames a star lives |
| `fps` | number | `60` | Frames per second |

## Examples

**More stars, faster:**
```json
{
  "app": "stars",
  "config": {
    "spawn_rate": 3,
    "lifetime": 50,
    "fps": 60
  }
}
```

**Slower, fewer stars:**
```json
{
  "app": "stars",
  "config": {
    "spawn_rate": 1,
    "lifetime": 80,
    "fps": 30
  }
}
```

**Dense starfield:**
```json
{
  "app": "stars",
  "config": {
    "spawn_rate": 5,
    "lifetime": 60
  }
}
```

**Update spawn rate while running:**
```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"spawn_rate": 10}'
```

## How It Works

- Each star is spawned at a random position with random RGB color
- Stars fade in and out using a sine wave for smooth animation
- Each star has an age counter that tracks its lifetime
- Stars are removed from the queue when they exceed their lifetime
- Higher spawn rates and longer lifetimes = more stars on screen at once
