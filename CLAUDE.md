# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Project

**Live vision assistant** (real-time card detection from screen):
```
python live_vision.py
```

**Command-line game** (manual card input):
```
python main.py
```

**Install dependencies:**
```
pip install -r requirements.txt
```

**Docker:**
```
docker build -t blackjack-ai .
docker run blackjack-ai
```

## Architecture

```
percent_engine.py  →  pre-calculates dealer outcome probabilities via recursive Monte Carlo
functions.py       →  interactive CLI blackjack game loop (manual card entry)
live_vision.py     →  screen capture → YOLO card detection → move recommendation
main.py            →  entry point (incomplete scaffold)
best.pt            →  pre-trained YOLO weights for card detection
```

### Probability Engine (`percent_engine.py`)
- `dealer_percent_engine(hand, deck)` — recursively walks all possible dealer draw sequences; populates `outcomes[upcard][final_sum]` with probabilities
- `get_best_move(player_hand, dealer_upcard)` — compares stand win rate vs. expected hit win rate; returns `"HIT"` or `"STAND"`
- `outcomes` is a module-level dict keyed `[dealer_upcard][dealer_final_sum]`; computed once at import time

### Live Vision (`live_vision.py`)
- Uses `mss` for full-screen capture, `ultralytics` YOLO for card detection
- Splits detected cards into dealer (top half of screen) vs. player (bottom half) by Y-coordinate threshold
- `hand_is_over` / `previous_card_count` flags prevent duplicate recommendations mid-hand
- Calls `get_best_move()` after each new card is detected

### Game Logic (`functions.py`)
- `shuffle_deck()` — returns list of card values (Aces as 11)
- `deal(deck)` — pops and returns top card
- `play()` — interactive loop; handles Ace conversion (11 → 1) when player busts
- Dealer hits on <17 per standard rules
