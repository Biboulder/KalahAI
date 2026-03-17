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


def run_tournament(depth=6, verbose=False):
    heuristics = [str(i) for i in range(5)]

    for h0 in heuristics:
        for h1 in heuristics:
            winner0 = play_game(h0, h1, starting_player=0, depth=depth, verbose=verbose)
            winner1 = play_game(h0, h1, starting_player=1, depth=depth, verbose=verbose)
            print(f"h0={h0} vs h1={h1}: start0→{winner0}, start1→{winner1}")


if __name__ == "__main__":
    print("Running heuristics tournament (5x5) with 2 games per pair...")
    run_tournament(depth=6, verbose=False)
