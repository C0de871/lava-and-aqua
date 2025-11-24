"""
Game Controller - Connects View and Model
Handles game loop, input, and state transitions
"""

import pygame
from enum import Enum
from models.player_factory import PlayerFactory
from views.menu_view import MenuView
from views.game_view import GameView
from views.file_chooser_view import FileChooserView
from views.dialog_view import DialogView
from models.direction_enum import Direction
from utils.board_loader import BoardLoader


class GameState(Enum):
    MENU = 1
    FILE_CHOOSER = 2
    PLAYING = 3
    WIN = 4
    DEATH = 5
    QUIT = 6


class GameController:
    def __init__(self):
        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        pygame.display.set_caption("Lava & Aqua")

        self.clock = pygame.time.Clock()
        self.fps = 60

        # Views
        self.menu_view = MenuView(self.screen)
        self.file_chooser_view = FileChooserView(self.screen)
        self.game_view = None
        self.dialog_view = DialogView(self.screen)

        # State
        self.state = GameState.MENU
        self.board = None
        self.move_count = 0

        # Action execution state (only exists while processing)
        self.executing_actions = False
        self.current_action_queue = []
        self.action_delay = 0.09  # 500 milliseconds
        self.time_since_last_action = 0

    def run(self):
        """Main game loop"""
        running = True

        while running:
            dt = self.clock.tick(self.fps) / 1000.0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self._handle_event(event)

            # Update
            self._update(dt)

            # Render
            self._render()

            pygame.display.flip()

            # Check if we should quit
            if self.state == GameState.QUIT:
                running = False

    def _handle_event(self, event):
        """Route events to appropriate handlers based on state"""
        if self.state == GameState.MENU:
            self._handle_menu_event(event)
        elif self.state == GameState.FILE_CHOOSER:
            self._handle_file_chooser_event(event)
        elif self.state == GameState.PLAYING:
            self._handle_playing_event(event)
        elif self.state in [GameState.WIN, GameState.DEATH]:
            self._handle_dialog_event(event)

    def _handle_menu_event(self, event):
        """Handle menu screen events"""
        result = self.menu_view.handle_event(event)
        if result:
            if result == "quit":
                self.state = GameState.QUIT
            else:
                self.player = PlayerFactory().getPlayer(result)
                self.state = GameState.FILE_CHOOSER

    def _handle_file_chooser_event(self, event):
        """Handle file chooser events"""
        result = self.file_chooser_view.handle_event(event)
        if result:
            if result == "back":
                self.state = GameState.MENU
            elif result.startswith("file:"):
                filepath = result[5:]
                self._load_board(filepath)

    def _handle_dialog_event(self, event):
        """Handle win/death dialog events"""
        title = "Victory!" if self.state == GameState.WIN else "Game Over"
        message = "You reached the gate!" if self.state == GameState.WIN else "You died in the lava!"

        result = self.dialog_view.handle_event(event, title, message)
        if result == "restart":
            if hasattr(self, 'current_board_file'):
                self._load_board(self.current_board_file)
        elif result == "quit":
            self.state = GameState.MENU

    def _handle_playing_event(self, event):
        """Handle in-game events"""
        if event.type == pygame.KEYDOWN:
            # Escape to return to menu
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
                return

            # R to reload board
            if event.key == pygame.K_r:
                if hasattr(self, 'current_board_file'):
                    self._load_board(self.current_board_file)
                return

        # Only get actions if not currently executing a sequence
        if not self.executing_actions:
            if self.board:
                directions = self.player.get_next_action(event, self.board)

            # Start executing the action sequence
            if directions:
                self.current_action_queue = directions
                self.executing_actions = True
                self.time_since_last_action = 0

                # Execute first action immediately (no delay before first)
                if self.current_action_queue:
                    first_direction = self.current_action_queue.pop(0)
                    self._execute_move(first_direction)

                    # If that was the only action, we're done
                    if not self.current_action_queue:
                        self.executing_actions = False

    def _update(self, dt):
        """Update game state"""
        if self.state == GameState.PLAYING and self.executing_actions:
            # Process remaining actions with delay between them
            self.time_since_last_action += dt

            if self.time_since_last_action >= self.action_delay:
                if self.current_action_queue:
                    # Execute next action
                    direction = self.current_action_queue.pop(0)
                    self._execute_move(direction)
                    self.time_since_last_action = 0

                    # If queue is empty, stop executing
                    if not self.current_action_queue:
                        self.executing_actions = False

    def _render(self):
        """Render current state"""
        self.screen.fill((50, 50, 50))

        if self.state == GameState.MENU:
            self.menu_view.render()
        elif self.state == GameState.FILE_CHOOSER:
            self.file_chooser_view.render()
        elif self.state == GameState.PLAYING:
            if self.game_view:
                self.game_view.render(self.board, self.move_count)
        elif self.state in [GameState.WIN, GameState.DEATH]:
            # Render game in background
            if self.game_view:
                self.game_view.render(self.board, self.move_count)

            # Render dialog on top
            title = "Victory!" if self.state == GameState.WIN else "Game Over"
            message = "You reached the gate!" if self.state == GameState.WIN else "You died in the lava!"
            self.dialog_view.render(title, message)

    def _load_board(self, filepath):
        """Load board from file"""
        try:
            loader = BoardLoader()
            self.board = loader.load_from_file(filepath, self.player)
            self.current_board_file = filepath
            self.move_count = 0
            # Clear any ongoing action execution
            self.executing_actions = False
            self.current_action_queue = []
            self.time_since_last_action = 0

            # Create game view
            self.game_view = GameView(self.screen)

            # Start playing
            self.state = GameState.PLAYING
            # Reset action queue

        except Exception as e:
            print(f"Error loading board: {e}")
            self.state = GameState.MENU

    def _execute_move(self, direction: Direction):
        """Execute a player move and update the world"""
        if not self.board or not self.board.is_player_alive():
            return

        # Execute the move (board.update handles everything)
        self.board.update(direction)
        self.move_count += 1

        # Check win/lose conditions
        if not self.board.is_player_alive():
            self.state = GameState.DEATH
        elif self.board.is_gate_reached():
            self.state = GameState.WIN
