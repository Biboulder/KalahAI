import math

def minimax(game, board, player, depth, ai_player, heuristic_val, alpha=-math.inf, beta=math.inf, weights=None):
    """
    Minimax search with Alpha–Beta pruning.

    Parameters
    ----------
    game:
        Object providing the game API:
          - game.is_game_over(board) -> bool
          - game.get_actions(board, player) -> list[int]
          - game.apply_move(board, player, pit) -> (new_board, new_player)
          - game.heuristic(board, ai_player, heuristic_val) -> float
    board:
        Current board state (list of 14 ints).
    player:
        Who is to move in this state (0 or 1).
    depth:
        Remaining search depth (int). When depth == 0, we evaluate using the heuristic.
    ai_player:
        Which player the AI is playing (0 or 1).
    heuristic_val:
        Which heuristic to use (e.g., "0", "1", "2", "3", "4", "combined").
    alpha:
        Best (highest) value MAX (AI) can guarantee so far along the current path.
    beta:
        Best (lowest) value MIN (opponent) can guarantee so far along the current path.
    """
    
    # If game is finished OR we've reached depth limit, return heuristic evaluation.
    if game.is_game_over(board) or depth == 0:
        return game.heuristic(board, ai_player, heuristic_val, weights), None

    best_move = None

    # --------------------------
    # MAX node: AI's turn
    # --------------------------
    if player == ai_player:
        best_val = -math.inf
        for pit in game.get_actions(board, player):
            new_board, new_player = game.apply_move(board, player, pit)
            
            # Recurse into the child state
            val, _ = minimax(game, new_board, new_player, depth-1, ai_player, heuristic_val, alpha, beta, weights)
            
            # Keep the best move for MAX
            if val > best_val:
                best_val, best_move = val, pit
            
            # Update alpha: MAX's best guaranteed value so far
            alpha = max(alpha, best_val)
            
            # B-cut: MIN already has a better (lower) option elsewhere,
            # so MAX will never choose something that allows MIN to force <= alpha.
            if beta <= alpha:
                break
        return best_val, best_move
    
    # --------------------------
    # MIN node: opponent's turn
    # --------------------------
    else:
        best_val = math.inf
        for pit in game.get_actions(board, player):
            new_board, new_player = game.apply_move(board, player, pit)
            val, _ = minimax(game, new_board, new_player, depth-1, ai_player, heuristic_val, alpha, beta, weights)
                        
            # Keep the best move for MIN (minimum value for AI)
            if val < best_val:
                best_val, best_move = val, pit

            # Update beta: MIN's best guaranteed value so far
            beta = min(beta, best_val)
            
            # Alpha cut: MAX already has an option >= beta elsewhere,
            # so MIN will avoid anything that lets MAX achieve >= beta.
            if beta <= alpha:
                break
        return best_val, best_move