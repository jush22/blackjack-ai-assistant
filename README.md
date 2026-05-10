# Blackjack AI Assistant

A real-time blackjack advisor that uses computer vision to detect cards on your screen and recommends the mathematically optimal move using Monte Carlo probability analysis.

---

## How It Works

1. **Card Detection** — A YOLO model continuously scans your screen and identifies playing cards in real time.
2. **Hand Parsing** — Detected cards are split into the dealer's hand (top of screen) and the player's hand (bottom of screen) based on screen position.
3. **Probability Engine** — A pre-computed Monte Carlo simulation calculates the dealer's probability of reaching every possible final sum (17–21 or bust) for each upcard.
4. **Recommendation** — The engine compares the win rate of standing vs. hitting and displays the optimal move on screen.

---

## Demo

| State | Display |
|---|---|
| Waiting for cards | `Waiting for cards...` |
| Recommendation | `HIT` (green) / `STAND` (orange) |
| Blackjack | `YOU WIN!` |
| Bust | `BUST!` |
| Stand locked | `STAND!` |

---

## Installation

**Requirements:** Python 3.9+

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `opencv-python` — display and overlay rendering
- `ultralytics` — YOLO card detection
- `mss` — multi-monitor screen capture
- `numpy` — numerical computation

---

## Usage

```bash
python3 live_vision.py
```

A window titled **Stake Blackjack Vision** will open showing your screen with an overlay panel at the top center.

### Controls

| Button | Action |
|---|---|
| **New Hand** | Reset and wait for the next hand |
| **Stop** | Close the assistant |

---

## Project Structure

```
├── live_vision.py       # Main entry point — screen capture, detection, overlay
├── percent_engine.py    # Monte Carlo probability engine
├── functions.py         # CLI blackjack game (manual card input)
├── best.pt              # Pre-trained YOLO weights for card detection
└── requirements.txt     # Python dependencies
```

---

## Configuration

In `live_vision.py`, three pixel thresholds control card region detection. Adjust these to match your screen layout:

```python
Y_coordinate = 650        # Y threshold separating dealer (above) from player (below)
left_X_coordinate = 700   # Left boundary of player hand region
right_X_coordinate = 900  # Right boundary of player hand region
```

---

## How the Probability Engine Works

At startup, `percent_engine.py` runs a recursive simulation for every possible dealer upcard (2–11). It walks every possible sequence of cards the dealer could draw, weighted by probability, and builds a lookup table:

```
outcomes[dealer_upcard][final_sum] → probability
```

`get_best_move(player_hand, dealer_upcard)` then compares:
- **Stand win rate** — probability dealer busts or finishes below your total
- **Hit win rate** — expected win probability across all possible next cards

The move with the higher win rate is recommended.

---

## License

MIT
