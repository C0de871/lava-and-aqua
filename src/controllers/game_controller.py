
from lib.models.board import Board


class GameController:
    """Controls game flow and state - Pure Logic"""
    
    def __init__(self, board: Board, is_player_mode: bool):
        self.board = board
        self.is_player_mode = is_player_mode
        self.game_over = False
        self.game_won = False
        
    def process_player_move(self, direction: str) -> bool:
        """Process a player move and execute turn"""
        if self.game_over:
            return False
        
        # Move player
        moved = self.board.move_player(direction)
        
        # Execute turn effects
        self.board.execute_turn(direction)
        
        # Check game state
        self.check_game_state()
        
        return moved
    
    def process_computer_move(self):
        """
        Process one computer move
        TODO: Implement AI algorithm (BFS, A*, etc.)
        """
        if self.game_over:
            return
        
        # TODO: Implement AI logic
        pass
    
    def check_game_state(self):
        """Check and update game state"""
        if self.board.check_win_condition():
            self.game_over = True
            self.game_won = True
        elif self.board.check_lose_condition():
            self.game_over = True
            self.game_won = False
