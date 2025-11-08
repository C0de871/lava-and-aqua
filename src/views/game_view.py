

from lib.controllers.game_controller import GameController
from lib.models.goal_cell import GoalCell
from lib.models.lava_cell import LavaCell
from lib.views.components.modern_button import ModernButton
from lib.models.numbered_wall_cell import NumberedWallCell
from lib.models.parmeable_wall_cell import PermeableWallCell
from lib.models.stone_cell import StoneCell
from lib.models.water_cell import WaterCell
import customtkinter as ctk


class GameView:
    """Modern UI for playing the game"""

    CELL_SIZE = 50

    def __init__(self, controller: GameController):
        self.controller = controller

        ctk.set_appearance_mode("dark")

        self.window = ctk.CTk()
        self.window.title("2D Board Game - Playing")

        # Main frame
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Info panel
        self.create_info_panel(main_frame)

        # Canvas
        canvas_frame = ctk.CTkFrame(main_frame)
        canvas_frame.pack(pady=20)

        self.canvas = ctk.CTkCanvas(
            canvas_frame,
            width=self.controller.board.cols * self.CELL_SIZE,
            height=self.controller.board.rows * self.CELL_SIZE,
            bg="#1A1A1A",
            highlightthickness=2,
            highlightbackground="#00D9FF"
        )
        self.canvas.pack()

        # Bind keyboard
        if controller.is_player_mode:
            self.window.bind("<Up>", lambda e: self.move_player("up"))
            self.window.bind("<Down>", lambda e: self.move_player("down"))
            self.window.bind("<Left>", lambda e: self.move_player("left"))
            self.window.bind("<Right>", lambda e: self.move_player("right"))

        self.draw_board()

        # Start computer if needed
        if not controller.is_player_mode:
            self.window.after(1000, self.computer_step)

    def create_info_panel(self, parent):
        """Create info panel"""
        info_frame = ctk.CTkFrame(parent)
        info_frame.pack(pady=10)

        mode = "👤 Player Mode" if self.controller.is_player_mode else "🤖 Computer Mode"

        ctk.CTkLabel(
            info_frame,
            text=mode,
            font=("Segoe UI", 20, "bold"),
            text_color="#00D9FF"
        ).pack(side="left", padx=20)

        self.turn_label = ctk.CTkLabel(
            info_frame,
            text=f"Turn: {self.controller.board.turn_count}",
            font=("Segoe UI", 16),
            text_color="#AAAAAA"
        )
        self.turn_label.pack(side="left", padx=20)

        if self.controller.is_player_mode:
            ctk.CTkLabel(
                info_frame,
                text="⌨️ Use Arrow Keys",
                font=("Segoe UI", 14),
                text_color="#AAAAAA"
            ).pack(side="left", padx=20)

    def draw_board(self):
        """Draw the game board"""
        self.canvas.delete("all")

        for row in range(self.controller.board.rows):
            for col in range(self.controller.board.cols):
                x1 = col * self.CELL_SIZE
                y1 = row * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE

                cell = self.controller.board.get_cell(row, col)
                color = cell.get_color()  # type: ignore

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="#333333",
                    width=1
                )

                # Draw numbered walls
                if isinstance(cell, NumberedWallCell):
                    self.canvas.create_text(
                        (x1 + x2) / 2, (y1 + y2) / 2,
                        text=str(cell.number),
                        font=("Segoe UI", 16, "bold"),
                        fill="white"
                    )

                # Draw symbols
                symbol_map = {
                    GoalCell: "★",
                    StoneCell: "●",
                    LavaCell: "~",
                    WaterCell: "≈",
                    PermeableWallCell: "▒"
                }

                for cell_class, symbol in symbol_map.items():
                    if isinstance(cell, cell_class):
                        self.canvas.create_text(
                            (x1 + x2) / 2, (y1 + y2) / 2,
                            text=symbol,
                            font=("Segoe UI", 20, "bold"),
                            fill="white"
                        )

        # Draw player
        if self.controller.board.player_pos:
            row, col = self.controller.board.player_pos
            x1 = col * self.CELL_SIZE
            y1 = row * self.CELL_SIZE
            x2 = x1 + self.CELL_SIZE
            y2 = y1 + self.CELL_SIZE

            self.canvas.create_oval(
                x1 + 8, y1 + 8, x2 - 8, y2 - 8,
                fill="#FFD700",
                outline="#FFA500",
                width=3
            )

        # Update turn counter
        self.turn_label.configure(text=f"Turn: {self.controller.board.turn_count}")

    def move_player(self, direction: str):
        """Handle player movement"""
        self.controller.process_player_move(direction)
        self.draw_board()
        self.check_game_state()

    def computer_step(self):
        """Execute one computer step"""
        if not self.controller.game_over:
            self.controller.process_computer_move()
            self.draw_board()
            self.check_game_state()
            self.window.after(500, self.computer_step)

    def check_game_state(self):
        """Check for win/lose"""
        if self.controller.game_over:
            if self.controller.game_won:
                self.show_result(
                    "🎉 Victory!", "You reached the goal!", "#00FF00")
            else:
                self.show_result("💀 Game Over", "You lost!", "#FF4444")

    def show_result(self, title: str, message: str, color: str):
        """Show game result dialog"""
        result_window = ctk.CTkToplevel(self.window)
        result_window.title(title)
        result_window.geometry("400x250")
        result_window.grab_set()

        frame = ctk.CTkFrame(result_window)
        frame.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(
            frame,
            text=title,
            font=("Segoe UI", 32, "bold"),
            text_color=color
        ).pack(pady=20)

        ctk.CTkLabel(
            frame,
            text=message,
            font=("Segoe UI", 16),
            text_color="#AAAAAA"
        ).pack(pady=10)

        ctk.CTkLabel(
            frame,
            text=f"Turns: {self.controller.board.turn_count}",
            font=("Segoe UI", 14),
            text_color="#AAAAAA"
        ).pack(pady=10)

        ModernButton(
            frame,
            text="Close",
            width=150,
            fg_color=color,
            hover_color=color,
            command=lambda: [result_window.destroy(), self.window.destroy()]
        ).pack(pady=20)

    def run(self):
        """Start the game window"""
        self.window.mainloop()
