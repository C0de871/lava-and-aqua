"""
Game Controller - Updated to work with enhanced animated views
Handles game loop, input, and state transitions
"""

from collections import deque
from multiprocessing import Process, Queue
import time
import pygame
from enum import Enum
from models.bfs_player import AiPlayer
from models.player_factory import PlayerFactory
from utils.zobrist_hash import Zobrist
from models.direction_enum import Direction
from utils.board_loader import BoardLoader

# Import the enhanced views
from views.console_renderer import ConsoleRenderer
from views.menu_view import MenuView
from views.game_view import GameView
from views.file_chooser_view import FileChooserView
from views.dialog_view import DialogView


class GameState(Enum):
    MENU = 1
    FILE_CHOOSER = 2
    PLAYING = 3
    WIN = 4
    DEATH = 5
    QUIT = 6


class GameController:
    def __init__(self):
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        pygame.display.set_caption("Lava & Aqua")

        self.clock = pygame.time.Clock()
        self.fps = 60

        # Views - using enhanced versions
        self.menu_view = MenuView(self.screen)
        self.file_chooser_view = FileChooserView(self.screen)
        self.game_view = None
        self.dialog_view = DialogView(self.screen)

        # State
        self.state = GameState.MENU
        self.board = None
        self.move_count = 0

        # Action execution state
        self.redo_stack = deque()
        self.executing_actions = False
        self.current_action_queue = []
        self.action_delay = 0.09
        self.time_since_last_action = 0
        self.result_queue = Queue()
        self.start = 0
        self.end = 0
        self.ai_time = 0
        self.explored_states_len = 0
        self.generated_states_len = 0
        self.path_length = 0

    def run(self):
        """Main game loop with animation updates"""
        running = True
        self._render()
        pygame.display.flip()

        while running:
            if not self.result_queue.empty():
                if isinstance(self.player, AiPlayer):
                    result = self.result_queue.get()
                    self.ai_time = result[0]
                    self.player.solution_path = result[1]
                    self.explored_states_len = result[2]
                    self.generated_states_len = result[3]
                    # Calculate path length
                    self.path_length = len(
                        self.player.solution_path) if self.player.solution_path else 0

            dt = self.clock.tick(self.fps) / 1000.0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self._handle_event(event)

            # Update animations
            self._update_animations(dt)

            # Update game logic
            self._update(dt)

            # Render
            self._render()
            pygame.display.flip()

            # Check if we should quit
            if self.state == GameState.QUIT:
                running = False

    def _update_animations(self, dt):
        """Update view animations"""
        if self.state == GameState.MENU:
            self.menu_view.update(dt)
        elif self.state == GameState.FILE_CHOOSER:
            self.file_chooser_view.update(dt)
        elif self.state == GameState.PLAYING or GameState.DEATH or GameState.WIN:
            if self.game_view:
                self.game_view.update(dt)

    def _handle_event(self, event):
        """Route events to appropriate handlers based on state"""
        if self.state == GameState.MENU:
            self._handle_menu_event(event)
        elif self.state == GameState.FILE_CHOOSER:
            self._handle_file_chooser_event(event)
        elif self.state == GameState.PLAYING:
            self._handle_playing_event(event)
        elif self.state in [GameState.WIN, GameState.DEATH]:
            # Handle restart/quit in win/death state
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if hasattr(self, 'current_board_file'):
                        self._load_board(self.current_board_file)
                elif event.key == pygame.K_z:
                    self.undo_move()
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU

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

    def _handle_playing_event(self, event):
        """Handle in-game events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
                return

            if event.key == pygame.K_r:
                if hasattr(self, 'current_board_file'):
                    self._load_board(self.current_board_file)
                return
            if event.key == pygame.K_z:
                self.undo_move()
                return

        # Only get actions if not currently executing a sequence
        if not self.executing_actions:
            if self.board:
                directions = self.player.get_next_action(event)

            if directions:
                self.current_action_queue = directions
                self.executing_actions = True
                self.time_since_last_action = 0

                # Execute first action immediately
                if self.current_action_queue:
                    first_direction = self.current_action_queue.pop(0)
                    self._execute_move(first_direction)

                    if not self.current_action_queue:
                        self.executing_actions = False

    def _update(self, dt):
        """Update game state"""
        if self.state == GameState.PLAYING and self.executing_actions:
            self.time_since_last_action += dt

            if self.time_since_last_action >= self.action_delay:
                if self.current_action_queue:
                    direction = self.current_action_queue.pop(0)
                    self._execute_move(direction)
                    self.time_since_last_action = 0

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
                self.game_view.render(
                    self.board,
                    self.move_count,
                    self.ai_time,
                    self.explored_states_len,
                    self.generated_states_len,
                    self.path_length,
                    "playing"
                )
        elif self.state in [GameState.WIN, GameState.DEATH]:
            if self.game_view:
                game_status = "win" if self.state == GameState.WIN else "death"
                self.game_view.render(
                    self.board,
                    self.move_count,
                    self.ai_time,
                    self.explored_states_len,
                    self.generated_states_len,
                    self.path_length,
                    game_status
                )

    def _load_board(self, filepath):
        """Load board from file"""
        try:
            loader = BoardLoader()
            self.player.revive()
            self.board = loader.load_from_file(filepath, self.player)
            self.current_board_file = filepath
            self.move_count = 0

            # Clear action execution state
            self.redo_stack = deque()
            self.executing_actions = False
            self.current_action_queue = []
            self.time_since_last_action = 0

            # Reset statistics
            self.ai_time = 0
            self.explored_states_len = 0
            self.generated_states_len = 0
            self.path_length = 0

            # Create enhanced game view
            self.game_view = GameView(self.screen)

            self.start = time.time()
            if isinstance(self.player, AiPlayer):
                p = Process(target=find_path, args=(
                    self.board, self.player, self.result_queue))
                p.start()

            ConsoleRenderer().render(self.board, self.move_count)

            self.state = GameState.PLAYING

        except Exception as e:
            print(f"Error loading board: {e}")
            self.state = GameState.MENU

    def _execute_move(self, direction: Direction):
        """Execute a player move and update the world"""
        if not self.board or self.board.is_player_touch_lava_or_wall():
            return

        # Store previous position for particle effects
        if self.game_view and self.board.player:
            prev_pos = self.board.player.position

        # Execute the move
        new_board = self.board.transition_model(direction)
        if (self.board != new_board):
            self.move_count += 1
            self.redo_stack.append(self.board)
            self.board = new_board

        ConsoleRenderer().render(self.board, self.move_count)

        # Add visual effects for special events
        if self.game_view and self.board.player:
            current_cell = self.board.get_cell(self.board.player.position)

            # Particle effects for lava/aqua
            if current_cell.startswith('L'):
                # Lava splash
                screen_x = (self.screen.get_width() -
                            self.board.col * self.game_view.TILE_SIZE) // 2
                screen_y = (self.screen.get_height() -
                            self.board.row * self.game_view.TILE_SIZE) // 2 + 30
                px = screen_x + self.board.player.position.x * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                py = screen_y + self.board.player.position.y * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                self.game_view.add_particles(px, py, (255, 100, 0), 10)
                self.game_view.screen_shake(5, 0.2)

            elif current_cell.startswith('A'):
                # Aqua splash
                screen_x = (self.screen.get_width() -
                            self.board.col * self.game_view.TILE_SIZE) // 2
                screen_y = (self.screen.get_height() -
                            self.board.row * self.game_view.TILE_SIZE) // 2 + 30
                px = screen_x + self.board.player.position.x * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                py = screen_y + self.board.player.position.y * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                self.game_view.add_particles(px, py, (0, 150, 255), 8)

        # Check win/lose conditions
        if self.board.is_player_touch_lava_or_wall():
            if self.state != GameState.DEATH:
                print(f"Game Over - Time: {self.end - self.start:.2f}s")
            self.state = GameState.DEATH
            if self.game_view:
                self.game_view.screen_shake(10, 0.5)
        elif self.board.is_gate_reached():
            if self.state != GameState.WIN:
                self.end = time.time()
                print(f"Victory! - Time: {self.end - self.start:.2f}s")
            self.state = GameState.WIN
            if self.game_view:
                # Victory particles
                screen_x = (self.screen.get_width() -
                            self.board.col * self.game_view.TILE_SIZE) // 2
                screen_y = (self.screen.get_height() -
                            self.board.row * self.game_view.TILE_SIZE) // 2 + 30
                px = screen_x + self.board.player.position.x * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                py = screen_y + self.board.player.position.y * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                self.game_view.add_particles(px, py, (255, 215, 0), 20)

    def undo_move(self):
        """Execute a player move and update the world"""
        if len(self.redo_stack) == 0:
            return

        self.state = GameState.PLAYING

        # Store previous position for particle effects
        if self.game_view and self.board and self.board.player:
            prev_pos = self.board.player.position

        new_board = self.redo_stack.pop()
        ConsoleRenderer().render(new_board, self.move_count)

        self.move_count -= 1
        self.board = new_board

        ConsoleRenderer().render(self.board, self.move_count)

        # Add visual effects for special events
        if self.game_view and self.board.player:
            current_cell = self.board.get_cell(self.board.player.position)

            # Particle effects for lava/aqua
            if current_cell.startswith('L'):
                # Lava splash
                screen_x = (self.screen.get_width() -
                            self.board.col * self.game_view.TILE_SIZE) // 2
                screen_y = (self.screen.get_height() -
                            self.board.row * self.game_view.TILE_SIZE) // 2 + 30
                px = screen_x + self.board.player.position.x * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                py = screen_y + self.board.player.position.y * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                self.game_view.add_particles(px, py, (255, 100, 0), 10)
                self.game_view.screen_shake(5, 0.2)

            elif current_cell.startswith('A'):
                # Aqua splash
                screen_x = (self.screen.get_width() -
                            self.board.col * self.game_view.TILE_SIZE) // 2
                screen_y = (self.screen.get_height() -
                            self.board.row * self.game_view.TILE_SIZE) // 2 + 30
                px = screen_x + self.board.player.position.x * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                py = screen_y + self.board.player.position.y * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                self.game_view.add_particles(px, py, (0, 150, 255), 8)

        # Check win/lose conditions
        if self.board.is_player_touch_lava_or_wall():
            if self.state != GameState.DEATH:
                self.end = time.time()
                print(f"Game Over - Time: {self.end - self.start:.2f}s")
            self.state = GameState.DEATH
            if self.game_view:
                self.game_view.screen_shake(10, 0.5)
        elif self.board.is_gate_reached():
            if self.state != GameState.WIN:
                self.end = time.time()
                print(f"Victory! - Time: {self.end - self.start:.2f}s")
            self.state = GameState.WIN
            if self.game_view:
                # Victory particles
                screen_x = (self.screen.get_width() -
                            self.board.col * self.game_view.TILE_SIZE) // 2
                screen_y = (self.screen.get_height() -
                            self.board.row * self.game_view.TILE_SIZE) // 2 + 30
                px = screen_x + self.board.player.position.x * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                py = screen_y + self.board.player.position.y * \
                    self.game_view.TILE_SIZE + self.game_view.TILE_SIZE // 2
                self.game_view.add_particles(px, py, (255, 215, 0), 20)


def find_path(board, player: AiPlayer, result_queue):
    """Helper function for AI pathfinding"""
    Zobrist.initTables(board.row, board.col)
    result = player.solve(board)
    result_queue.put(result)
