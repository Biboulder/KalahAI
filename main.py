from kalah import Kalah
from minimax import minimax
 
AI_PLAYER = 1
DEPTH = 6
heuristic_val = "0"  # "0","1","2","3","4","combined"
    
def render_board(board):
    """
    Pretty board renderer for CLI.
    board indices:
      P0 pits: 0..5, store 6
      P1 pits: 7..12, store 13
    """
    p0_pits = board[0:6]
    p1_pits = board[7:13]
    p0_store = board[6]
    p1_store = board[13]

    top = "  ".join(f"{x:2d}" for x in reversed(p1_pits))
    bot = "  ".join(f"{x:2d}" for x in p0_pits)

    lines = []
    lines.append("\n" + "-" * 28)
    lines.append("  AI side")
    lines.append(f"      [{top}]")
    lines.append(f"  {p1_store:2d}                           {p0_store:2d} ")
    lines.append(f"      [{bot}]")
    lines.append("  You side")
    lines.append("-" * 28 + "\n")
    return "\n".join(lines)

def main():
    """
    CLI version of Kalah:
    - Human plays as Player 0
    - AI plays as Player 1
    """
   
    game = Kalah()
    print("Welcome to KalahAI!")
    print(f"AI settings: depth={DEPTH}, heuristic={heuristic_val}")
    # print(game)
    
    while not game.is_game_over(game.board):
        print(render_board(game.board))

        # AI turn
        if game.current_player == AI_PLAYER:
            _, pit = minimax(
                game, game.board, game.current_player,
                depth=DEPTH, ai_player=AI_PLAYER, heuristic_val=heuristic_val
            )
            print(f" --- AI plays pit {pit} ---")
            game.move(pit)
            # print(game)

        # Human turn
        else:
            try:
                pit_index = int(input("Your turn! Choose a pit (0-5): "))
                if pit_index < 0 or pit_index > 5:
                    print("\n !!! Please choose a number between 0 and 5 !!!")
                    continue
                print(f" --- You play pit {pit_index} ---")
                game.move(pit_index)
                # print(game)
            except ValueError as e:
                print(e)

    # End game
    print(render_board(game.board))
    winner = game.get_winner()
    if winner == -1:
        print("It's a tie! Well played!")
    elif winner == 0:
        print("You win!! Congratulations!")
    else:
        print("AI wins!! Better luck next time!")


if __name__ == "__main__":
    main()