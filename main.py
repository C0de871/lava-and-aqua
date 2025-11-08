

from typing import Optional
from lib.models.board import Board
from lib.views.board_construct_view import BoardConstructorView
from lib.controllers.game_controller import GameController
import customtkinter as ctk

from lib.views.game_mode_view import GameModeView
from lib.views.game_view import GameView
# ==================== APPLICATION ORCHESTRATOR ====================


class GameApplication:
    """Main application orchestrator - coordinates the flow"""

    def __init__(self):
        self.is_player_mode = False
        self.board: Optional[Board] = None

    def start(self):
        """Start the application flow"""
        # Step 1: Select game mode
        mode_view = GameModeView(self.on_mode_selected)
        mode_view.run()

    def on_mode_selected(self, is_player: bool):
        """Handle mode selection"""
        self.is_player_mode = is_player

        # Step 2: Get board dimensions
        dialog = ctk.CTkInputDialog(
            text="Enter number of rows (5-30):",
            title="Board Size"
        )
        rows_str = dialog.get_input()

        if not rows_str or not rows_str.isdigit():
            return

        rows = int(rows_str)
        if rows < 5 or rows > 30:
            return

        dialog = ctk.CTkInputDialog(
            text="Enter number of columns (5-30):",
            title="Board Size"
        )
        cols_str = dialog.get_input()

        if not cols_str or not cols_str.isdigit():
            return

        cols = int(cols_str)
        if cols < 5 or cols > 30:
            return

        # Step 3: Construct board
        constructor_view = BoardConstructorView(
            rows, cols, self.on_board_complete)
        constructor_view.run()

    def on_board_complete(self, board: Board):
        """Handle board construction completion"""
        self.board = board

        # Step 4: Start game
        controller = GameController(board, self.is_player_mode)
        game_view = GameView(controller)
        game_view.run()


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    app = GameApplication()
    app.start()
