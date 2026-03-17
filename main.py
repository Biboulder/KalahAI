from kalah import Kalah
from minimax import minimax

if __name__ == "__main__":
    AI_PLAYER = 1
    game = Kalah()
    print(game)
    while not game.is_game_over(game.board):
        if game.current_player == AI_PLAYER:
            _, pit = minimax(game, game.board, game.current_player, depth=6, ai_player=AI_PLAYER)
            print(f"AI plays pit {pit}")
            game.move(pit)
            print(game)
        try:
            pit_index = int(input(f"Select a pit (0-5): "))
            game.move(pit_index)
            print(game)
        except ValueError as e:
            print(e)
    
    winner = game.get_winner()
    if winner == -1:
        print("The game is a tie!")
    else:
        print(f"Player {winner} wins!")