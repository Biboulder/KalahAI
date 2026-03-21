from kalah import Kalah
from minimax import minimax


def play_game(heur0, heur1, starting_player, depth=6, verbose=False):
    """Play a single game between two AIs that use different heuristics.

    Returns the winner (0, 1, or -1 for tie).
    """

    game = Kalah()
    game.current_player = starting_player

    while not game.is_game_over(game.board):
        player = game.current_player
        heur = heur0 if player == 0 else heur1
        _, pit = minimax(game, game.board, player, depth, ai_player=player, heuristic_val=heur)
        game.move(pit)
        if verbose:
            print(f"Player {player} (h={heur}) plays pit {pit}")
            print(game)

    return game.get_winner()

def run_tournament(depth, verbose=False):
    heuristics = [str(i) for i in range(5)]
    # Track wins per heuristic: stats[heuristic_id] = win count
    heuristic_names = ['more_balls_in_pits', 'mobility', 'extra_turn_potential', 'capture_potential', 'weighted_pit_value']
    stats = {str(i): 0 for i in range(5)}
    ties = 0

    for i in range(len(heuristics)):
        for j in range(i + 1, len(heuristics)):  # Only play each unique pair once
            h0 = heuristics[i]
            h1 = heuristics[j]
                
            winner0 = play_game(h0, h1, starting_player=0, depth=depth, verbose=verbose)
            winner1 = play_game(h0, h1, starting_player=1, depth=depth, verbose=verbose)
            
            # Game 1: Player 0 (h0) vs Player 1 (h1), starting with Player 0
            if winner0 == 0:
                stats[h0] += 1  # h0 won
            elif winner0 == 1:
                stats[h1] += 1  # h1 won
            elif winner0 == -1:
                ties += 1  # tie
            
            # Game 2: Player 0 (h0) vs Player 1 (h1), starting with Player 1
            if winner1 == 0:
                stats[h0] += 1  # h0 won (Player 0 uses h0)
            elif winner1 == 1:
                stats[h1] += 1  # h1 won (Player 1 uses h1)
            elif winner1 == -1:
                ties += 1  # tie
            
            print(f"h{h0} vs h{h1}: start 0 → wins {winner0}, start 1 → wins {winner1}")

    print(f"\n--- Heuristic Win Summary ---")
    for h_id, wins in stats.items():
        print(f"Heuristic {h_id} ({heuristic_names[int(h_id)]}): {wins} wins")
    print(f"Ties: {ties}")
    print(f"Total games: {sum(stats.values()) + ties}")

    stats2 = {str(i): 0 for i in range(5)}
    stats2['combined'] = 0
    ties = 0  # Reset ties for combined tournament section
    print(f"\nNow testing combined weighted heuristic against each individual heuristic...")

    for i in range(len(heuristics)):

        winner0 = play_game('combined', heuristics[i], starting_player=0, depth=depth, verbose=verbose)
        winner1 = play_game('combined', heuristics[i], starting_player=1, depth=depth, verbose=verbose)

        if winner0 == 0:
            stats2['combined'] += 1  # combined won
        elif winner0 == 1:
            stats2[heuristics[i]] += 1  # individual heuristic won
        elif winner0 == -1:
            ties += 1  # tie

        if winner1 == 0:
            stats2['combined'] += 1  # combined won
        elif winner1 == 1:
            stats2[heuristics[i]] += 1  # individual heuristic won
        elif winner1 == -1:
            ties += 1  # tie

        print(f"Combined vs h{heuristics[i]}: start 0 → wins {winner0}, start 1 → wins {winner1}")

    print(f"\n--- Performance with Combined Heuristic ---")
    for h_id, wins in stats2.items():
        name = 'combined' if h_id == 'combined' else heuristic_names[int(h_id)]
        print(f"Heuristic {h_id} ({name}): {wins} wins")
    print(f"Ties: {ties}")
    print(f"Total games: {sum(stats2.values()) + ties}")
    
    

if __name__ == "__main__":
    print("Running heuristics tournament (5x5) with 2 games per pair...")
    for depth in [4, 6, 8, 10]:
        print(f"\n=== Tournament at Depth {depth} ===")
        run_tournament(depth=depth)
