# Kalah game implementation in Python
from random import randint

class Kalah:
    def __init__(self):
        # Initialize the board with 6 pits for each player and 1 store for each player
        self.board = [4] * 6 + [0] + [4] * 6 + [0]
        self.current_player = randint(0, 1)  # Randomly select the starting player

    def move(self, pit_index):
        if pit_index < 0 or pit_index > 5:
            raise ValueError("Invalid pit index. Must be between 0 and 5.")
        
        # Calculate the actual index on the board
        actual_index = pit_index if self.current_player == 0 else pit_index + 7
        
        if self.board[actual_index] == 0:
            raise ValueError("Selected pit is empty. Choose a different pit.")
        
        # Pick up the seeds from the selected pit
        seeds = self.board[actual_index]
        self.board[actual_index] = 0
        
        # Distribute the seeds
        index = actual_index
        while seeds > 0:
            index = (index + 1) % len(self.board)
            if (self.current_player == 0 and index == 13) or (self.current_player == 1 and index == 6):
                continue  # Skip opponent's store
            self.board[index] += 1
            seeds -= 1

        # Check for capture
        if (self.current_player == 0 and index < 6 and self.board[index] == 1) or (self.current_player == 1 and index > 6 and index < 13 and self.board[index] == 1):
            opposite_index = 12 - index
            if self.board[opposite_index] > 0:
                self.board[6 if self.current_player == 0 else 13] += self.board[opposite_index] + 1
                self.board[index] = 0
                self.board[opposite_index] = 0

        # Check for extra turn
        if (self.current_player == 0 and index == 6) or (self.current_player == 1 and index == 13):
            pass  # Player gets an extra turn
        else:
            self.current_player = 1 - self.current_player  # Switch players


    def is_game_over(self):
        return all(seeds == 0 for seeds in self.board[:6]) or all(seeds == 0 for seeds in self.board[7:13])
    
    def get_winner(self):
        if not self.is_game_over():
            return None  # Game is not over yet
        player0_score = self.board[6] + sum(self.board[:6])
        player1_score = self.board[13] + sum(self.board[7:13])
        if player0_score > player1_score:
            return 0  # Player 0 wins
        elif player1_score > player0_score:
            return 1  # Player 1 wins
        else:
            return -1  # It's a tie
        
    def __str__(self): 
        return f"Player 1: {self.board[13]} | {' '.join(map(str, self.board[7:13]))} | Player 0: {self.board[6]} | {' '.join(map(str, self.board[:6]))}"
    
# Example usage
if __name__ == "__main__":
    game = Kalah()
    print(game)
    while not game.is_game_over():
        try:
            pit_index = int(input(f"Player {game.current_player}, select a pit (0-5): "))
            game.move(pit_index)
            print(game)
        except ValueError as e:
            print(e)
    
    winner = game.get_winner()
    if winner == -1:
        print("The game is a tie!")
    else:
        print(f"Player {winner} wins!")