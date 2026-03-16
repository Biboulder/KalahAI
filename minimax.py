import math

def minimax(game, board, player, depth, ai_player, alpha=-math.inf, beta=math.inf):
    if game.is_game_over(board) or depth == 0:
        return game.heuristic(board, ai_player), None

    best_move = None
    if player == ai_player:
        best_val = -math.inf
        for pit in game.get_actions(board, player):
            new_board, new_player = game.apply_move(board, player, pit)
            val, _ = minimax(game, new_board, new_player, depth-1, ai_player, alpha, beta)
            if val > best_val:
                best_val, best_move = val, pit
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break  # β-cut
        return best_val, best_move
    else:
        best_val = math.inf
        for pit in game.get_actions(board, player):
            new_board, new_player = game.apply_move(board, player, pit)
            val, _ = minimax(game, new_board, new_player, depth-1, ai_player, alpha, beta)
            if val < best_val:
                best_val, best_move = val, pit
            beta = min(beta, best_val)
            if beta <= alpha:
                break  # α-cut
        return best_val, best_move