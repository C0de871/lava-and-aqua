"""
Game View - Renders the game board
"""

import pygame
from models.lava import Lava
from models.aqua import Aqua
from models.solid_wall import SolidWall
from models.count_down_wall import CountDownWall
from models.stone import Stone


class GameView:
    TILE_SIZE = 48

    def __init__(self, screen):
        self.screen = screen
        self.font_hud = pygame.font.Font(None, 32)
        self.font_wall = pygame.font.Font(None, 36)

        # Colors
        self.color_empty1 = (240, 240, 240)
        self.color_empty2 = (250, 250, 250)
        self.color_lava = (255, 100, 0)
        self.color_aqua = (0, 50, 150)
        self.color_wall = (80, 80, 100)
        self.color_stone = (120, 120, 120)
        self.color_key = (200, 150, 255)
        self.color_gate = (150, 100, 200)
        self.color_player = (255, 200, 100)

        # Try to load assets (optional)
        self.assets = {}
        self._load_assets()

    def _load_assets(self):
        """Try to load tile assets (optional)"""
        # Placeholder for asset loading
        # If assets exist in assets/ folder, load them here
        pass

    def render(self, board, move_count):
        """Render the entire game state"""
        self.screen.fill((30, 30, 30))

        # Calculate board position (center on screen)
        board_width = board.col * self.TILE_SIZE
        board_height = board.row * self.TILE_SIZE
        offset_x = (self.screen.get_width() - board_width) // 2
        offset_y = (self.screen.get_height() - board_height) // 2 + 30

        # Render grid
        for y in range(board.row):
            for x in range(board.col):
                screen_x = offset_x + x * self.TILE_SIZE
                screen_y = offset_y + y * self.TILE_SIZE

                from models.position import Position
                pos = Position(x, y)
                cell = board.get_cell_atpos(pos)

                self._render_tile(screen_x, screen_y, x, y, cell, board, pos)

        # Render HUD
        self._render_hud(move_count)

    def _render_tile(self, screen_x, screen_y, grid_x, grid_y, cell, board, pos):
        """Render a single tile"""
        rect = pygame.Rect(screen_x, screen_y, self.TILE_SIZE, self.TILE_SIZE)

        # Ground layer
        if isinstance(cell.ground, Lava):
            pygame.draw.rect(self.screen, self.color_lava, rect)
        elif isinstance(cell.ground, Aqua):
            pygame.draw.rect(self.screen, self.color_aqua, rect)
        else:  # Empty
            # Checkerboard pattern
            color = self.color_empty1 if (
                grid_x + grid_y) % 2 == 0 else self.color_empty2
            pygame.draw.rect(self.screen, color, rect)

        # Entity layer
        if cell.entity:
            if isinstance(cell.entity, SolidWall):
                if cell.entity.is_permeable:
                    # Pass-through wall: four corner squares
                    corner_size = 8
                    corner_color = (100, 100, 120)

                    # Top-left
                    pygame.draw.rect(self.screen, corner_color,
                                     (screen_x + 2, screen_y + 2, corner_size, corner_size))
                    # Top-right
                    pygame.draw.rect(self.screen, corner_color,
                                     (screen_x + self.TILE_SIZE - corner_size - 2, screen_y + 2,
                                      corner_size, corner_size))
                    # Bottom-left
                    pygame.draw.rect(self.screen, corner_color,
                                     (screen_x + 2, screen_y + self.TILE_SIZE - corner_size - 2,
                                      corner_size, corner_size))
                    # Bottom-right
                    pygame.draw.rect(self.screen, corner_color,
                                     (screen_x + self.TILE_SIZE - corner_size - 2,
                                      screen_y + self.TILE_SIZE - corner_size - 2,
                                      corner_size, corner_size))
                else:
                    # Solid wall
                    pygame.draw.rect(self.screen, self.color_wall, rect)

            elif isinstance(cell.entity, CountDownWall):
                # Numbered wall
                pygame.draw.rect(self.screen, self.color_wall, rect)
                count_text = self.font_wall.render(
                    str(cell.entity.count_down), True, (255, 255, 255))
                text_rect = count_text.get_rect(center=rect.center)
                self.screen.blit(count_text, text_rect)

            elif isinstance(cell.entity, Stone):
                # Box with four corner dots
                stone_rect = rect.inflate(-4, -4)
                pygame.draw.rect(self.screen, self.color_stone, stone_rect)

                # Four corner dots (nails)
                dot_size = 4
                dot_color = (80, 80, 80)
                dots = [
                    (screen_x + 6, screen_y + 6),
                    (screen_x + self.TILE_SIZE - 6, screen_y + 6),
                    (screen_x + 6, screen_y + self.TILE_SIZE - 6),
                    (screen_x + self.TILE_SIZE - 6, screen_y + self.TILE_SIZE - 6)
                ]
                for dot_x, dot_y in dots:
                    pygame.draw.circle(self.screen, dot_color,
                                       (dot_x, dot_y), dot_size)

        # Key
        if pos in board.keys:
            key_radius = 8
            key_center = (screen_x + self.TILE_SIZE // 2,
                          screen_y + self.TILE_SIZE // 2 - 5)
            pygame.draw.circle(self.screen, self.color_key,
                               key_center, key_radius)
            pygame.draw.circle(self.screen, (180, 120, 230),
                               key_center, key_radius, 2)

        # Gate
        if pos == board.gate_pos:
            gate_size = 30
            gate_rect = pygame.Rect(screen_x + (self.TILE_SIZE - gate_size) // 2,
                                    screen_y + (self.TILE_SIZE -
                                                gate_size) // 2,
                                    gate_size, gate_size)
            pygame.draw.rect(self.screen, self.color_gate,
                             gate_rect, 4, border_radius=3)
            inner_rect = gate_rect.inflate(-8, -8)
            pygame.draw.rect(self.screen, self.color_gate,
                             inner_rect, 2, border_radius=2)

        # Player
        if board.player.position == pos:
            player_radius = 16
            player_center = (screen_x + self.TILE_SIZE // 2,
                             screen_y + self.TILE_SIZE // 2)

            # Body
            pygame.draw.circle(self.screen, self.color_player,
                               player_center, player_radius)
            pygame.draw.circle(self.screen, (200, 150, 80),
                               player_center, player_radius, 2)

            # Eyes
            eye_color = (50, 50, 50)
            eye_radius = 3
            left_eye = (player_center[0] - 6, player_center[1] - 3)
            right_eye = (player_center[0] + 6, player_center[1] - 3)
            pygame.draw.circle(self.screen, eye_color, left_eye, eye_radius)
            pygame.draw.circle(self.screen, eye_color, right_eye, eye_radius)

        # Grid lines (subtle)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    def _render_hud(self, move_count):
        """Render HUD information"""
        hud_text = f"Moves: {move_count}  |  ESC: Menu  |  R: Restart"
        text_surface = self.font_hud.render(hud_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(
            center=(self.screen.get_width() // 2, 20))
        self.screen.blit(text_surface, text_rect)
