"""
Modern 2D Board Game with Clean Architecture
Separates UI from Logic and uses CustomTkinter for beautiful modern GUI
"""

import customtkinter as ctk
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
from abc import ABC, abstractmethod
import copy


# ==================== LOGIC LAYER ====================

class CellBase(ABC):
    """Base class for all cell types"""
    
    def __init__(self):
        self.color = "#FFFFFF"
        self.display_char = " "
    
    @abstractmethod
    def can_player_enter(self) -> bool:
        """Can the player move into this cell?"""
        pass
    
    @abstractmethod
    def can_spread_through(self) -> bool:
        """Can lava/water spread through this cell?"""
        pass
    
    @abstractmethod
    def on_turn_update(self):
        """Called every turn to update cell state"""
        pass
    
    def get_color(self) -> str:
        """Get the cell's display color"""
        return self.color
    
    def __repr__(self):
        return self.__class__.__name__


class EmptyCell(CellBase):
    """Empty cell - player can move through"""
    
    def __init__(self):
        super().__init__()
        self.color = "#2B2D31"
        self.display_char = "·"
    
    def can_player_enter(self) -> bool:
        return True
    
    def can_spread_through(self) -> bool:
        return True
    
    def on_turn_update(self):
        pass


class WallCell(CellBase):
    """Solid wall - blocks everything"""
    
    def __init__(self):
        super().__init__()
        self.color = "#4A4A4A"
        self.display_char = "█"
    
    def can_player_enter(self) -> bool:
        return False
    
    def can_spread_through(self) -> bool:
        return False
    
    def on_turn_update(self):
        pass


class LavaCell(CellBase):
    """Lava cell - deadly to player, spreads each turn"""
    
    def __init__(self):
        super().__init__()
        self.color = "#FF4444"
        self.display_char = "~"
    
    def can_player_enter(self) -> bool:
        return False  # Player dies if enters
    
    def can_spread_through(self) -> bool:
        return False
    
    def on_turn_update(self):
        """TODO: Implement lava spreading logic"""
        pass
    
    def spread(self, board, row: int, col: int):
        """TODO: Spread lava to adjacent cells"""
        pass


class WaterCell(CellBase):
    """Water cell - spreads each turn"""
    
    def __init__(self):
        super().__init__()
        self.color = "#4444FF"
        self.display_char = "≈"
    
    def can_player_enter(self) -> bool:
        return False
    
    def can_spread_through(self) -> bool:
        return False
    
    def on_turn_update(self):
        """TODO: Implement water spreading logic"""
        pass
    
    def spread(self, board, row: int, col: int):
        """TODO: Spread water to adjacent cells"""
        pass


class StoneCell(CellBase):
    """Stone - can be pushed by player in certain conditions"""
    
    def __init__(self):
        super().__init__()
        self.color = "#8B4513"
        self.display_char = "●"
    
    def can_player_enter(self) -> bool:
        return False
    
    def can_spread_through(self) -> bool:
        return False
    
    def on_turn_update(self):
        pass
    
    def can_be_pushed(self, board, from_row: int, from_col: int, 
                     to_row: int, to_col: int) -> bool:
        """TODO: Check if stone can be pushed in the given direction"""
        pass
    
    def push(self, board, from_row: int, from_col: int, 
            direction_row: int, direction_col: int):
        """TODO: Push stone in the given direction"""
        pass


class NumberedWallCell(CellBase):
    """Wall with a countdown number - becomes empty when reaches 0"""
    
    def __init__(self, number: int):
        super().__init__()
        self.number = number
        self.color = "#9B59B6"
        self.display_char = str(number)
    
    def can_player_enter(self) -> bool:
        return False
    
    def can_spread_through(self) -> bool:
        return False
    
    def on_turn_update(self):
        """TODO: Decrease number each turn"""
        pass
    
    def decrease(self):
        """TODO: Decrease the number and return True if should become empty"""
        pass
    
    def __repr__(self):
        return f"NumberedWall({self.number})"


class GoalCell(CellBase):
    """Goal gate - player wins when reaching this"""
    
    def __init__(self):
        super().__init__()
        self.color = "#00FF00"
        self.display_char = "★"
    
    def can_player_enter(self) -> bool:
        return True
    
    def can_spread_through(self) -> bool:
        return False
    
    def on_turn_update(self):
        pass


class PermeableWallCell(CellBase):
    """Wall that lava/water can spread through but nothing else can pass"""
    
    def __init__(self):
        super().__init__()
        self.color = "#A9A9A9"
        self.display_char = "▒"
    
    def can_player_enter(self) -> bool:
        return False
    
    def can_spread_through(self) -> bool:
        return True  # Only lava/water can spread through
    
    def on_turn_update(self):
        pass


class Board:
    """Game board managing all cells and game state - Pure Logic"""
    
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[CellBase]] = [[EmptyCell() for _ in range(cols)] 
                                            for _ in range(rows)]
        self.player_pos: Optional[Tuple[int, int]] = None
        self.goal_pos: Optional[Tuple[int, int]] = None
        self.turn_count = 0
        
    def set_cell(self, row: int, col: int, cell: CellBase):
        """Set a cell at the given position"""
        if self.is_valid_position(row, col):
            self.grid[row][col] = cell
            
    def get_cell(self, row: int, col: int) -> Optional[CellBase]:
        """Get the cell at the given position"""
        if self.is_valid_position(row, col):
            return self.grid[row][col]
        return None
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within bounds"""
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def set_player_position(self, row: int, col: int):
        """Set the player's starting position"""
        if self.is_valid_position(row, col):
            self.player_pos = (row, col)
        
    def set_goal_position(self, row: int, col: int):
        """Set the goal gate position"""
        if self.is_valid_position(row, col):
            self.goal_pos = (row, col)
            self.set_cell(row, col, GoalCell())
    
    def move_player(self, direction: str) -> bool:
        """
        Move player in the given direction
        TODO: Implement full movement logic:
        - Check if target cell allows entry
        - Handle stone pushing
        - Update player position
        - Return True if move succeeded
        """
        if not self.player_pos:
            return False
        
        # Direction vectors
        directions = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1)
        }
        
        if direction not in directions:
            return False
        
        # TODO: Implement actual movement logic here
        return False
    
    def execute_turn(self, player_direction: Optional[str] = None):
        """
        Execute one complete turn
        TODO: Implement turn execution:
        1. Move player if direction given
        2. Spread all lava cells
        3. Spread all water cells
        4. Update all numbered walls
        5. Check win/lose conditions
        """
        self.turn_count += 1
        
        # TODO: Implement turn logic
        pass
    
    def check_win_condition(self) -> bool:
        """Check if player reached the goal"""
        if self.player_pos and self.goal_pos:
            return self.player_pos == self.goal_pos
        return False
    
    def check_lose_condition(self) -> bool:
        """
        Check if player lost (touched lava, etc.)
        TODO: Implement lose condition checking
        """
        # TODO: Implement lose condition
        return False
    
    def get_adjacent_positions(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get valid adjacent positions (up, down, left, right)"""
        adjacent = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                adjacent.append((new_row, new_col))
        return adjacent


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


class BoardBuilder:
    """Builds and validates game boards - Pure Logic"""
    
    def __init__(self, rows: int, cols: int):
        self.board = Board(rows, cols)
        
    def place_cell(self, row: int, col: int, cell_type: str, number: int = 0):
        """Place a cell on the board"""
        cell_map = {
            "empty": EmptyCell(),
            "wall": WallCell(),
            "lava": LavaCell(),
            "water": WaterCell(),
            "stone": StoneCell(),
            "numbered_wall": NumberedWallCell(number),
            "goal": GoalCell(),
            "permeable_wall": PermeableWallCell()
        }
        
        if cell_type in cell_map:
            if cell_type == "goal":
                self.board.set_goal_position(row, col)
            else:
                self.board.set_cell(row, col, cell_map[cell_type])
    
    def set_player_start(self, row: int, col: int):
        """Set player starting position"""
        self.board.set_player_position(row, col)
    
    def validate_board(self) -> Tuple[bool, str]:
        """Validate that board is playable"""
        if not self.board.player_pos:
            return False, "Player starting position not set"
        
        if not self.board.goal_pos:
            return False, "Goal gate not set"
        
        return True, "Board is valid"
    
    def get_board(self) -> Board:
        """Get the constructed board"""
        return self.board


# ==================== UI LAYER ====================

class ModernButton(ctk.CTkButton):
    """Custom styled button for the game"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            corner_radius=10,
            font=("Segoe UI", 14, "bold"),
            height=45,
            **kwargs
        )


class GameModeView:
    """Modern UI for game mode selection"""
    
    def __init__(self, on_mode_selected):
        self.on_mode_selected = on_mode_selected
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.window = ctk.CTk()
        self.window.title("Game Mode Selection")
        self.window.geometry("600x400")
        
        # Main frame
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="🎮 2D Board Game",
            font=("Segoe UI", 36, "bold"),
            text_color="#00D9FF"
        )
        title.pack(pady=(0, 20))
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text="Who will play the game?",
            font=("Segoe UI", 18),
            text_color="#AAAAAA"
        )
        subtitle.pack(pady=(0, 50))
        
        # Button frame
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        # Player button
        player_btn = ModernButton(
            btn_frame,
            text="👤 Player",
            width=200,
            fg_color="#00D9FF",
            hover_color="#00B8E6",
            command=lambda: self.select_mode(True)
        )
        player_btn.pack(side="left", padx=15)
        
        # Computer button
        computer_btn = ModernButton(
            btn_frame,
            text="🤖 Computer",
            width=200,
            fg_color="#9B59B6",
            hover_color="#8E44AD",
            command=lambda: self.select_mode(False)
        )
        computer_btn.pack(side="left", padx=15)
        
    def select_mode(self, is_player: bool):
        """Handle mode selection"""
        self.window.destroy()
        self.on_mode_selected(is_player)
        
    def run(self):
        """Start the window"""
        self.window.mainloop()


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
                self.builder.place_cell(row, col, self.selected_type, int(number))
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
                color = cell.get_color()
                
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


class GameView:
    """Modern UI for playing the game"""
    
    CELL_SIZE = 50
    
    def __init__(self, controller: GameController):
        self.controller = controller
        self.board = controller.board
        
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
            width=self.board.cols * self.CELL_SIZE,
            height=self.board.rows * self.CELL_SIZE,
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
            text=f"Turn: {self.board.turn_count}",
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
        
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                x1 = col * self.CELL_SIZE
                y1 = row * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE
                
                cell = self.board.get_cell(row, col)
                color = cell.get_color()
                
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
        if self.board.player_pos:
            row, col = self.board.player_pos
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
        self.turn_label.configure(text=f"Turn: {self.board.turn_count}")
    
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
                self.show_result("🎉 Victory!", "You reached the goal!", "#00FF00")
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
            text=f"Turns: {self.board.turn_count}",
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
        constructor_view = BoardConstructorView(rows, cols, self.on_board_complete)
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
    """
    Installation required:
    pip install customtkinter
    
    This uses CustomTkinter for modern, beautiful UI
    """
    app = GameApplication()
    app.start()