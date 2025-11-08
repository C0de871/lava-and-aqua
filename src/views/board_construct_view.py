import customtkinter as ctk
from typing import Optional, Tuple
from lib.models.goal_cell import GoalCell
from lib.models.lava_cell import LavaCell
from lib.logic.board_builder import BoardBuilder
from lib.views.components.modern_button import ModernButton
from lib.models.numbered_wall_cell import NumberedWallCell
from lib.models.parmeable_wall_cell import PermeableWallCell
from lib.models.stone_cell import StoneCell
from lib.models.water_cell import WaterCell


class BoardConstructorView:
    """Modern UI for board construction"""

    CELL_SIZE = 50

    CELL_COLORS = {
        "empty": "#2B2D31",
        "wall": "#4A4A4A",
        "lava": "#FF4444",
        "water": "#4444FF",
        "stone": "#8B4513",
        "numbered_wall": "#9B59B6",
        "goal": "#00FF00",
        "permeable_wall": "#A9A9A9",
        "player": "#FFD700"
    }

    def __init__(self, rows: int, cols: int, on_board_complete):
        self.builder = BoardBuilder(rows, cols)
        self.on_board_complete = on_board_complete
        self.selected_type = "wall"
        self.is_drawing = False

        ctk.set_appearance_mode("dark")

        self.window = ctk.CTk()
        self.window.title("Board Constructor")

        # Main container
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="🎨 Design Your Board",
            font=("Segoe UI", 28, "bold"),
            text_color="#00D9FF"
        )
        title.pack(pady=(0, 20))

        # Control panel
        self.create_control_panel(main_frame)

        # Canvas frame
        canvas_frame = ctk.CTkFrame(main_frame)
        canvas_frame.pack(pady=20)

        # Canvas
        self.canvas = ctk.CTkCanvas(
            canvas_frame,
            width=cols * self.CELL_SIZE,
            height=rows * self.CELL_SIZE,
            bg="#1A1A1A",
            highlightthickness=2,
            highlightbackground="#00D9FF"
        )
        self.canvas.pack()

        # Bind events
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Start button
        start_btn = ModernButton(
            main_frame,
            text="▶ Start Game",
            width=300,
            height=50,
            fg_color="#00FF00",
            hover_color="#00CC00",
            text_color="#000000",
            font=("Segoe UI", 16, "bold"),
            command=self.start_game
        )
        start_btn.pack(pady=20)

        self.draw_board()

    def create_control_panel(self, parent):
        """Create cell type selection panel"""
        panel = ctk.CTkFrame(parent)
        panel.pack(pady=10)

        ctk.CTkLabel(
            panel,
            text="Select Cell Type:",
            font=("Segoe UI", 14, "bold")
        ).pack(side="left", padx=10)

        cell_types = [
            ("🧱 Wall", "wall", "#4A4A4A"),
            ("🔥 Lava", "lava", "#FF4444"),
            ("💧 Water", "water", "#4444FF"),
            ("🪨 Stone", "stone", "#8B4513"),
            ("🔢 Numbered", "numbered_wall", "#9B59B6"),
            ("⭐ Goal", "goal", "#00FF00"),
            ("▒ Permeable", "permeable_wall", "#A9A9A9"),
            ("👤 Player", "player", "#FFD700"),
            ("⬜ Empty", "empty", "#2B2D31")
        ]

        for label, cell_type, color in cell_types:
            btn = ModernButton(
                panel,
                text=label,
                width=120,
                height=35,
                fg_color=color,
                hover_color=color,
                text_color="#FFFFFF" if cell_type != "goal" else "#000000",
                font=("Segoe UI", 11, "bold"),
                command=lambda ct=cell_type: self.select_cell_type(ct)
            )
            btn.pack(side="left", padx=3)

    def select_cell_type(self, cell_type: str):
        """Select cell type for placement"""
        self.selected_type = cell_type

    def get_cell_coords(self, event) -> Optional[Tuple[int, int]]:
        """Convert canvas coordinates to grid coordinates"""
        col = event.x // self.CELL_SIZE
        row = event.y // self.CELL_SIZE
        if self.builder.board.is_valid_position(row, col):
            return (row, col)
        return None

    def on_mouse_down(self, event):
        """Handle mouse press"""
        self.is_drawing = True
        self.place_cell(event)

    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if self.is_drawing:
            self.place_cell(event)

    def on_mouse_up(self, event):
        """Handle mouse release"""
        self.is_drawing = False

    def place_cell(self, event):
        """Place cell at mouse position"""
        coords = self.get_cell_coords(event)
        if not coords:
            return

        row, col = coords

        if self.selected_type == "numbered_wall":
            # Ask for number
            dialog = ctk.CTkInputDialog(
                text="Enter wall number (1-99):",
                title="Numbered Wall"
            )
            number = dialog.get_input()
            if number and number.isdigit():
                self.builder.place_cell(
                    row, col, self.selected_type, int(number))
        elif self.selected_type == "player":
            self.builder.set_player_start(row, col)
        else:
            self.builder.place_cell(row, col, self.selected_type)

        self.draw_board()

    def draw_board(self):
        """Draw the board on canvas"""
        self.canvas.delete("all")
        board = self.builder.board

        for row in range(board.rows):
            for col in range(board.cols):
                x1 = col * self.CELL_SIZE
                y1 = row * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE

                cell = board.get_cell(row, col)
                color = cell.get_color()  # type: ignore

                # Draw cell
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="#333333",
                    width=1
                )

                # Draw number for numbered walls
                if isinstance(cell, NumberedWallCell):
                    self.canvas.create_text(
                        (x1 + x2) / 2, (y1 + y2) / 2,
                        text=str(cell.number),
                        font=("Segoe UI", 16, "bold"),
                        fill="white"
                    )

                # Draw symbol
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
        if board.player_pos:
            row, col = board.player_pos
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

    def start_game(self):
        """Validate and start game"""
        valid, message = self.builder.validate_board()
        if not valid:
            # Show error dialog
            dialog = ctk.CTkInputDialog(text=message, title="Error")
            return

        self.window.destroy()
        self.on_board_complete(self.builder.get_board())

    def run(self):
        """Start the window"""
        self.window.mainloop()
