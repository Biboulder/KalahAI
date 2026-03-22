import random
from itertools import product
from kalah import Kalah
from minimax import minimax

DEPTH = 6
HEURISTIC_NAMES = {
    '0': 'store_diff',
    '1': 'mobility',
    '2': 'extra_turn',
    '3': 'capture',
    '4': 'weighted_pits',
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def random_valid_board():
    """Play random moves from s0 to get a valid mid-game board."""
    game = Kalah()
    for _ in range(random.randint(5, 30)):
        if game.is_game_over(game.board):
            break
        actions = game.get_actions(game.board, game.current_player)
        if not actions:
            break
        game.move(random.choice(actions))
    return game.board.copy(), game.current_player


def play_game(heur0, heur1, starting_player, depth=DEPTH, board=None):
    """Play one game. If board is given, start from that state."""
    game = Kalah()
    game.current_player = starting_player
    if board is not None:
        game.board = board.copy()

    while not game.is_game_over(game.board):
        player = game.current_player
        heur = heur0 if player == 0 else heur1
        _, pit = minimax(game, game.board, player, depth,
                         ai_player=player, heuristic_val=heur)
        if pit is None:
            break
        game.move(pit)

    return game.get_winner()


def play_match(h0, h1, boards, depth=DEPTH):
    """
    Play h0 vs h1 on a list of (board, start) states.
    Each board is played twice — once per side — to remove first-player bias.
    Returns (wins_h0, wins_h1, ties).
    """
    w0 = w1 = ties = 0
    for board, start in boards:
        # h0 as player 0
        r = play_game(h0, h1, start, depth, board)
        if r == 0:        w0   += 1
        elif r == 1:      w1   += 1
        else:             ties += 1
        # h1 as player 0 (swap)
        r = play_game(h1, h0, start, depth, board)
        if r == 0:        w1   += 1
        elif r == 1:      w0   += 1
        else:             ties += 1
    return w0, w1, ties


# ── Step 1: full heuristic tournament ─────────────────────────────────────────

def run_tournament(depth=DEPTH):
    heuristics = [str(i) for i in range(5)]
    stats = {h: 0 for h in heuristics}
    ties  = 0

    print(f"\n{'='*55}")
    print(f"STEP 1 — Heuristic tournament (depth={depth}, 2 games/pair)")
    print(f"{'='*55}")

    for i in range(len(heuristics)):
        for j in range(i + 1, len(heuristics)):
            h0, h1 = heuristics[i], heuristics[j]
            w0 = play_game(h0, h1, starting_player=0, depth=depth)
            w1 = play_game(h0, h1, starting_player=1, depth=depth)

            if w0 == 0:   stats[h0] += 1
            elif w0 == 1: stats[h1] += 1
            else:         ties += 1

            if w1 == 0:   stats[h0] += 1
            elif w1 == 1: stats[h1] += 1
            else:         ties += 1

            print(f"  h{h0} ({HEURISTIC_NAMES[h0]}) vs "
                  f"h{h1} ({HEURISTIC_NAMES[h1]}): "
                  f"start0={w0}  start1={w1}")

    print(f"\n--- Standings ---")
    for h, w in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {HEURISTIC_NAMES[h]:<20} {w} wins")
    print(f"  Ties: {ties}")




# ── Step 2: random-state evaluation ───────────────────────────────────────────

def run_random_state_eval(n_boards=50, depth=DEPTH):
    """
    Generate 50 random board states.
    Each pair of heuristics plays on every board (both sides) = 100 games/pair.
    This gives a statistically solid win rate.
    """
    print(f"\n{'='*55}")
    print(f"STEP 2 — Random-state evaluation")
    print(f"Boards: {n_boards}  Games/pair: {n_boards*2}  Depth: {depth}")
    print(f"{'='*55}")

    boards = [random_valid_board() for _ in range(n_boards)]
    heuristics = [str(i) for i in range(5)]
    stats = {h: 0 for h in heuristics}
    ties  = 0

    print(f"{'Matchup':<40} {'H0 wins':>8} {'H1 wins':>8} {'Ties':>6}")
    print("-" * 65)

    for i in range(len(heuristics)):
        for j in range(i + 1, len(heuristics)):
            h0, h1 = heuristics[i], heuristics[j]
            w0, w1, t = play_match(h0, h1, boards, depth)
            stats[h0] += w0
            stats[h1] += w1
            ties      += t
            label = f"{HEURISTIC_NAMES[h0]} vs {HEURISTIC_NAMES[h1]}"
            print(f"  {label:<38} {w0:>8} {w1:>8} {t:>6}")

    print(f"\n--- Final standings ---")
    for h, w in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {HEURISTIC_NAMES[h]:<20} {w} wins")
    print(f"  Ties: {ties}")

    # return heuristics that beat store_diff (h0)
    baseline_wins = stats['0']
    survivors = [h for h in heuristics
                 if h != '0' and stats[h] > baseline_wins]
    print(f"\nHeuristics that beat baseline: "
          f"{[HEURISTIC_NAMES[h] for h in survivors] or 'none'}")
    return survivors, boards


# ── Step 3: grid search for best weights ──────────────────────────────────────

def play_game_weighted(w0, w1, board, start, depth=DEPTH):
    game = Kalah()
    game.board = board.copy()
    game.current_player = start

    while not game.is_game_over(game.board):
        player  = game.current_player
        weights = w0 if player == 0 else w1
        _, pit  = minimax(game, game.board, player, depth,
                          ai_player=player, heuristic_val='weighted',
                          weights=weights)
        if pit is None:
            break
        game.move(pit)

    return game.get_winner()


def match_weighted(w0, w1, boards, depth=DEPTH):
    wins0 = wins1 = ties = 0
    for board, start in boards:
        r = play_game_weighted(w0, w1, board, start, depth)
        if r == 0:        wins0 += 1
        elif r == 1:      wins1 += 1
        else:             ties  += 1
        # swap sides
        r = play_game_weighted(w1, w0, board, start, depth)
        if r == 0:        wins1 += 1
        elif r == 1:      wins0 += 1
        else:             ties  += 1
    return wins0, wins1, ties


def run_grid_search(boards, depth=DEPTH):
    """
    Coarse grid: weights in [0, 0.5, 1.0, 1.5, 2.0]
    Baseline = (1, 0, 0, 0, 0) = pure store_diff.
    """
    baseline = (1.0, 0.0, 0.0, 0.0, 0.0)

    coarse_vals = [0.0, 0.5, 1.0, 1.5, 2.0]
    combos      = list(product(coarse_vals, repeat=5))

    print(f"\n{'='*55}")
    print(f"STEP 3A — Coarse grid search")
    print(f"Values: {coarse_vals}  Combinations: {len(combos)}")
    print(f"Games/pair: {len(boards)*2}  Depth: {depth}")
    print(f"{'='*55}")

    best_wins   = -1
    best_combo  = baseline

    for w in combos:
        if w == baseline:
            continue
        wins, _, _ = match_weighted(w, baseline, boards, depth)
        if wins > best_wins:
            best_wins  = wins
            best_combo = w
            total = len(boards) * 2
            print(f"  New best: {w}  "
                  f"win rate={wins}/{total} ({wins/total:.0%})")

    print(f"\nBest coarse weights: {best_combo}  "
          f"({best_wins}/{len(boards)*2} wins vs baseline)")

    total = len(boards) * 2
    print(f"\n{'='*55}")
    print(f"BEST WEIGHTS FOUND (coarse search)")
    print(f"{'='*55}")
    labels = ['store_diff', 'mobility', 'extra_turn', 'capture', 'weighted_pits']
    for label, val in zip(labels, best_combo):
        print(f"  {label:<20} {val}")
    print(f"  Win rate vs baseline: {best_wins}/{total} ({best_wins/total:.0%})")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Running heuristics tournament (5x5) with 2 games per pair...")
    for depth in [4, 6, 8, 10]:
        print(f"\n=== Tournament at Depth {depth} ===")
        run_tournament(depth=depth)

    print("\n\nGenerating 50 random board states for evaluation...")
    survivors, boards = run_random_state_eval(n_boards=50, depth=6)

    print("\n\nRunning grid search for best weight combinatio on 30 random boards...")
    grid_boards = [random_valid_board() for _ in range(30)]  # separate 30 boards for grid search
    run_grid_search(grid_boards, depth=4)