# KalahAI

A playable implementation of the board game **Kalah (Kalaha)** with an AI opponent using **Minimax with Alpha–Beta pruning**.

## Requirements
- Python 3.10+ recommended
- Pygame (for GUI mode)

Install pygame:
```bash
pip install pygame
```

## Run CLI Version (main.py)
```bash
python main.py
```
## Run GUI Version (GUI.py)
```bash
python gui.py
```

## Project Structure
- `kalah.py` — Game logic + heuristics
- `minimax.py` — Minimax with alpha–beta pruning
- `main.py` — CLI game loop (human vs AI)
- `gui.py` — Pygame user interface
- `testbench.py` — Runs AI vs AI tournaments to compare heuristics

## Features
- Classic Kalah rules (6 pits per side + 1 store per player)
- Human vs AI
- AI uses **Minimax with Alpha–Beta pruning**
- Multiple heuristic evaluation functions (selectable)
    - Store difference (baseline)
    - Mobility (number of legal moves)
    - Extra-turn potential
    - Capture potential
    - Weighted pit value (stones closer to store count more)
    - Weighted **combination** of multiple heuristics
- Two ways to play:
  - CLI (terminal)
  - Pygame GUI

## AI Depth
THe AI search strength is mainly controlled by the **depth** parameter passed to `minimax()`.
- Where to change it:
    - In main.py, edit the `DEPTH`
    - In gui.py, edit the `AI_DEPTH`
- Typical values:
    - depth = 4  -> fast
    - depth = 6  -> balanced
    - depth = 8+ -> stronger but may become slow depending on the machine

## Heuristics
The AI uses a heuristic evaluation function at the leaf nodes of the search tree.
- In main.py, change heuristic_val to one of: `"0", "1", "2", "3", "4", or "combined"`
- In gui.py, change `AI_HEURISTIC` to one of the same values.

## Tournament (testbench.py)
To compare heuristics automatically:
```bash
python testbench.py
```

## Attribution
- `gui.py` is adapted from an existing Pygame Kalah GUI found online. We modified it to integrate with our `Kalah` game logic.