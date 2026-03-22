# Kalah game implementation in Python
from random import randint
from minimax import minimax

class Kalah:
    def __init__(self):
        """
        Board (length 14 list):
        - Player 0 pits: indices 0..5
        - Player 0 store: index 6
        - Player 1 pits: indices 7..12
        - Player 1 store: index 13
        """
        self.board = [4] * 6 + [0] + [4] * 6 + [0]
        self.current_player = randint(0, 1)  # Randomly select the starting player (0 or 1)

    def apply_move(self,board, player, pit_index):
        """
        Apply a move for `player` choosing relative pit `pit_index` (0..5).
        
        Parameters:
            board: current board state (list of 14 ints)
            player: 0 or 1
            pit_index: 0..5 (relative pit index on player's side)

        Returns:
            (new_board, new_player)
        
        - If the last seed lands in the player's store, the player gets an extra turn,
        so new_player can be the same as player (extra turn rule).
        """
        new_board = board.copy()
        new_player = player

        if pit_index < 0 or pit_index > 5:
            raise ValueError("Invalid pit index. Must be between 0 and 5.")
        
        # --- Calculate the actual index on the board ---
        actual_index = pit_index if new_player == 0 else pit_index + 7
        
        if new_board[actual_index] == 0:
            raise ValueError("Selected pit is empty. Choose a different pit.")
        
        # --- Pick up all seeds from the selected pit ---
        seeds = new_board[actual_index]
        new_board[actual_index] = 0
        
        # --- Distribute the seeds ---
        index = actual_index
        while seeds > 0:
            index = (index + 1) % len(new_board)
            
            # --- Skip opponent's store ---
            # - if player 0 is moving, skip store 13
            # - if player 1 is moving, skip store 6
            if (new_player == 0 and index == 13) or (new_player == 1 and index == 6):
                continue  
            
            new_board[index] += 1
            seeds -= 1

        # --- Capture rule ---
        # If player's last seed lands in an empty pit, player capture that last seed
        # plus all seeds in the opposite pit and place them in their store.
        #
        # This implementation checks: "after sowing, the landing pit has exactly 1 seed"
        # which means it was empty before the last seed was dropped (in the typical case).
        if (
            (new_player == 0 and index < 6 and new_board[index] == 1) 
            or (new_player == 1 and index > 6 and index < 13 and new_board[index] == 1)
        ):
            opposite_index = 12 - index # pit opposite mapping
            if new_board[opposite_index] > 0:
                new_board[6 if new_player == 0 else 13] += new_board[opposite_index] + 1
                new_board[index] = 0
                new_board[opposite_index] = 0
        
        # --- Extra turn rule ---
        # If last seed lands in player's store, player moves again.
        if (new_player == 0 and index == 6) or (new_player == 1 and index == 13):
            pass 
        else:
            new_player = 1 - new_player  # Switch players

        # --- End-of-game sweep ---
        # If either player's pits are all empty, the game ends.
        # All remaining seeds on the other side are moved into that player's store.
        if all(b == 0 for b in new_board[:6]) or all(b == 0 for b in new_board[7:13]):
            for i in range(6):
                new_board[6]  += new_board[i]
                new_board[i]   = 0
                new_board[13] += new_board[7 + i]
                new_board[7+i] = 0

        return new_board, new_player
    
    def move(self, pit_index):
        """Apply a move to the current internal state (used for human/GUI play)."""
        new_board, new_player = self.apply_move(self.board,self.current_player, pit_index)
        self.board = new_board
        self.current_player = new_player

    def is_game_over(self, board):
        """Game ends when all pits on either side are empty."""
        return all(b == 0 for b in board[:6]) or all(b == 0 for b in board[7:13])
    
    def get_winner(self):
        """Return 0 if player 0 wins, 1 if player 1 wins, -1 for tie """
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
    
    # -------------------------
    # Heuristics (Evaluation)
    # -------------------------
    # Each heuristic returns a higher value for positions that are better for `ai_player`.
    # The heuristic selector in `heuristic()` chooses which one to use.

    def more_balls_in_pits(self, board, ai_player):
        """Heuristic 0: difference in store stones."""
        if ai_player == 0:
            return board[6] - board[13]
        else:
            return board[13] - board[6]

    def mobility(self, board, ai_player):
        """Heuristic 1: number of legal moves (mobility) difference."""
        own_moves = len(self.get_actions(board, ai_player))
        opp_moves = len(self.get_actions(board, 1 - ai_player))
        return own_moves - opp_moves

    def extra_turn_potential(self, board, ai_player):
        """Heuristic 2: extra-turn potential difference.
        Counts how many legal moves would end in the player's store (extra turn),
        minus how many extra-turn moves the opponent has.- opponent getting extra turns
        """
        opponent = 1 - ai_player

        # Count legal moves that keep the turn (last seed lands in own store).
        ai_extra_turns = 0
        for pit in self.get_actions(board, ai_player):
            _, next_player = self.apply_move(board, ai_player, pit)
            if next_player == ai_player:
                ai_extra_turns = ai_extra_turns + 1

        opp_extra_turns = 0
        for pit in self.get_actions(board, opponent):
            _, next_player = self.apply_move(board, opponent, pit)
            if next_player == opponent:
                opp_extra_turns = opp_extra_turns + 1

        return ai_extra_turns - opp_extra_turns

    def capture_potential(self, board, ai_player):
        """Heuristic 3: capture potential.
        Counts how many moves increase the AI store by more than 1 seed (suggesting a capture)."""
        store_index = 6 if ai_player == 0 else 13
        base_store = board[store_index]
        captures = 0
        for pit in self.get_actions(board, ai_player):
            new_board, _ = self.apply_move(board, ai_player, pit)
            if new_board[store_index] - base_store > 1:
                captures += 1
        return captures

    def weighted_pit_value(self, board, ai_player):
        """Heuristic 4: weighted pit distribution.
        Stones closer to the store are weighted more highly (encourages building towards scoring).
        """
        if ai_player == 0:
            own_range = range(6)
            opp_range = range(7, 13)
        else:
            own_range = range(7, 13)
            opp_range = range(6)

        def weighted_sum(pits, weights):
            return sum(stones * weight for stones, weight in zip(pits, weights))

        # For own pits, give higher weight to pits closer to the store.
        own_weights = list(range(1, 7)) if ai_player == 0 else list(range(6, 0, -1))
        opp_weights = list(reversed(own_weights))

        own_score = weighted_sum([board[i] for i in own_range], own_weights)
        opp_score = weighted_sum([board[i] for i in opp_range], opp_weights)
        return own_score - opp_score
    
    def combine_heuristics(self, board, ai_player):
        """Combine multiple heuristics into one score.
        """
        h0 = self.more_balls_in_pits(board, ai_player)
        h1 = self.mobility(board, ai_player)
        h2 = self.extra_turn_potential(board, ai_player)
        h3 = self.capture_potential(board, ai_player)
        h4 = self.weighted_pit_value(board, ai_player)

        # Simple weighted sum of heuristics (weights can be tuned).
        return 0.70 * h0 + 0.05 * h1 + 0.10 * h2 + 0.10 * h3 + 0.05 * h4

    def heuristic(self, board, ai_player, val):
        """
        Dispatch method to select which heuristic to use.

        val can be:
        "0", "1", "2", "3", "4", or "combined"
        """
        val = str(val)
        match val:
            case "0":
                return self.more_balls_in_pits(board, ai_player)
            case "1":
                return self.mobility(board, ai_player)
            case "2":
                return self.extra_turn_potential(board, ai_player)
            case "3":
                return self.capture_potential(board, ai_player)
            case "4":
                return self.weighted_pit_value(board, ai_player)
            case "combined":
                return self.combine_heuristics(board, ai_player)
            case _:
                raise ValueError(f"Unknown heuristic value: {val}")
    
    def __str__(self): 
        """
        Pretty-print board.
        Note: this assumes Player 1 is the AI and Player 0 is the human ("YOU").
        """
        return f"AI: {self.board[13]} | {' '.join(map(str, self.board[7:13]))} | YOU: {self.board[6]} | {' '.join(map(str, self.board[:6]))}"

