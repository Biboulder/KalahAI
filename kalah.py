# Kalah game implementation in Python
from random import randint
from minimax import minimax

class Kalah:
    def __init__(self):
        # Initialize the board with 6 pits for each player and 1 store for each player
        self.board = [4] * 6 + [0] + [4] * 6 + [0]
        self.current_player = randint(0, 1)  # Randomly select the starting player

    def apply_move(self,board, player, pit_index):
        new_board = board.copy()
        new_player = player

        if pit_index < 0 or pit_index > 5:
            raise ValueError("Invalid pit index. Must be between 0 and 5.")
        
        # Calculate the actual index on the board
        actual_index = pit_index if new_player == 0 else pit_index + 7
        
        if new_board[actual_index] == 0:
            raise ValueError("Selected pit is empty. Choose a different pit.")
        
        # Pick up the seeds from the selected pit
        seeds = new_board[actual_index]
        new_board[actual_index] = 0
        
        # Distribute the seeds
        index = actual_index
        while seeds > 0:
            index = (index + 1) % len(new_board)
            if (new_player == 0 and index == 13) or (new_player == 1 and index == 6):
                continue  # Skip opponent's store
            new_board[index] += 1
            seeds -= 1

        # Check for capture
        if (new_player == 0 and index < 6 and new_board[index] == 1) or (new_player == 1 and index > 6 and index < 13 and new_board[index] == 1):
            opposite_index = 12 - index
            if new_board[opposite_index] > 0:
                new_board[6 if new_player == 0 else 13] += new_board[opposite_index] + 1
                new_board[index] = 0
                new_board[opposite_index] = 0
        # Check for extra turn
        if (new_player == 0 and index == 6) or (new_player == 1 and index == 13):
            pass  # Player gets an extra turn
        else:
            new_player = 1 - new_player  # Switch players

         # End-of-game sweep
        if all(b == 0 for b in new_board[:6]) or all(b == 0 for b in new_board[7:13]):
            for i in range(6):
                new_board[6]  += new_board[i]
                new_board[i]   = 0
                new_board[13] += new_board[7 + i]
                new_board[7+i] = 0

        return new_board, new_player
    
    def move(self, pit_index):
        new_board, new_player = self.apply_move(self.board,self.current_player, pit_index)
        self.board = new_board
        self.current_player = new_player


    def is_game_over(self, board):
        return all(b == 0 for b in board[:6]) or all(b == 0 for b in board[7:13])
    
    def get_winner(self):
        if not self.is_game_over(self.board):
            return None
        if self.board[6] > self.board[13]:
            return 0
        elif self.board[13] > self.board[6]:
            return 1
        else:
            return -1
        
    def get_actions(self, board, player):
        start = 0 if player == 0 else 7
        return [i for i in range(6) if board[start + i] > 0]
    
    # easy heuristic that only checks how many balls in the kalah
    # more implementations:
    # - possibility of extra turn
    # - possibility to capture opponents beans
    # - pit distribution -> more balls in different pits is better -> more moves
    # - beans close to kalah are more valuable
    # - count the opponents captures in the next turn
    def heuristic(self, board, ai_player):
        if ai_player == 0:
            return board[6] - board[13]
        else:
            return board[13] - board[6]

    def __str__(self): 
        return f"AI: {self.board[13]} | {' '.join(map(str, self.board[7:13]))} | YOU: {self.board[6]} | {' '.join(map(str, self.board[:6]))}"
    
# Example usage
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

