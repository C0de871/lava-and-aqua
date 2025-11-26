"""
Game View - Enhanced with beautiful animations and visual effects
"""

import pygame
import math
from models.board import Board


class ParticleEffect:
    """Simple particle for visual effects"""
    def __init__(self, x, y, color, velocity, lifetime=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = 3
    
    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += 0.2  # Gravity
        self.lifetime -= dt
        return self.lifetime > 0
    
    def render(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = int(self.size * (self.lifetime / self.max_lifetime))
        if size > 0:
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], alpha)
            pygame.draw.circle(s, color_with_alpha, (size, size), size)
            screen.blit(s, (int(self.x - size), int(self.y - size)))


class AnimatedSprite:
    """Handles position animations for game objects"""
    def __init__(self, x, y):
        self.target_x = x
        self.target_y = y
        self.current_x = float(x)
        self.current_y = float(y)
        self.speed = 8.0
    
    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y
    
    def update(self, dt):
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0.5:
            move = min(self.speed * dt * 60, dist)
            self.current_x += (dx / dist) * move
            self.current_y += (dy / dist) * move
        else:
            self.current_x = self.target_x
            self.current_y = self.target_y
    
    def get_pos(self):
        return (int(self.current_x), int(self.current_y))


class GameView:
    TILE_SIZE = 48

    def __init__(self, screen):
        self.screen = screen
        self.font_hud = pygame.font.Font(None, 36)
        self.font_wall = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        # Enhanced color palette with gradients
        self.color_empty1 = (245, 245, 250)
        self.color_empty2 = (235, 235, 245)
        self.color_lava = (255, 80, 20)
        self.color_lava_dark = (200, 40, 0)
        self.color_aqua = (30, 150, 255)
        self.color_aqua_dark = (10, 100, 200)
        self.color_wall = (60, 65, 80)
        self.color_stone = (140, 145, 150)
        self.color_stone_shadow = (100, 105, 110)
        self.color_key = (255, 215, 0)
        self.color_gate = (138, 43, 226)
        self.color_player = (255, 180, 60)
        
        # Animation state
        self.time = 0
        self.player_sprite = None
        self.particles = []
        self.shake_intensity = 0
        self.shake_duration = 0
        
        # Cache for rendered surfaces
        self.tile_cache = {}
        
    def add_particles(self, x, y, color, count=5):
        """Add particle effect at position"""
        import random
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2
            self.particles.append(ParticleEffect(x, y, color, (vx, vy), random.uniform(0.5, 1.0)))
    
    def screen_shake(self, intensity=5, duration=0.2):
        """Trigger screen shake effect"""
        self.shake_intensity = intensity
        self.shake_duration = duration

    def update(self, dt):
        """Update animations"""
        self.time += dt
        
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
            if self.shake_duration <= 0:
                self.shake_intensity = 0
        
        # Update player sprite
        if self.player_sprite:
            self.player_sprite.update(dt)

    def render(self, board, move_count, ai_time=0, explored_states=0, generated_states=0, path_length=0, game_status="playing"):
        """Render the entire game state with animations and statistics"""
        
        # Animated gradient background
        for y in range(0, self.screen.get_height(), 4):
            progress = y / self.screen.get_height()
            wave = math.sin(self.time * 0.5 + progress * 2) * 5
            color = (
                int(20 + progress * 15 + wave),
                int(22 + progress * 18 + wave),
                int(30 + progress * 25)
            )
            pygame.draw.rect(self.screen, color, (0, y, self.screen.get_width(), 4))
        
        # Calculate shake offset
        shake_x = 0
        shake_y = 0
        if self.shake_intensity > 0:
            import random
            shake_x = random.randint(-self.shake_intensity, self.shake_intensity)
            shake_y = random.randint(-self.shake_intensity, self.shake_intensity)

        # Calculate board position (center on screen)
        board_width = board.col * self.TILE_SIZE
        board_height = board.row * self.TILE_SIZE
        offset_x = (self.screen.get_width() - board_width) // 2 + shake_x
        offset_y = (self.screen.get_height() - board_height) // 2 + 30 + shake_y

        # Initialize player sprite if needed
        if self.player_sprite is None and board.player:
            px = offset_x + board.player.position.x * self.TILE_SIZE + self.TILE_SIZE // 2
            py = offset_y + board.player.position.y * self.TILE_SIZE + self.TILE_SIZE // 2
            self.player_sprite = AnimatedSprite(px, py)

        # Render grid with depth
        for y in range(board.row):
            for x in range(board.col):
                screen_x = offset_x + x * self.TILE_SIZE
                screen_y = offset_y + y * self.TILE_SIZE

                from models.position import Position
                pos = Position(x, y)
                cell = board.get_cell(pos)

                self._render_tile(screen_x, screen_y, x, y, cell, board, pos)

        # Render particles on top
        for particle in self.particles:
            particle.render(self.screen)

        # Render statistics panel
        self._render_statistics_panel(ai_time, explored_states, generated_states, path_length, game_status, offset_x, board_width)

        # Render HUD
        self._render_hud(move_count)

    def _render_tile(self, screen_x, screen_y, grid_x, grid_y, cell: str, board, pos):
        """Render a single tile with enhanced graphics"""
        rect = pygame.Rect(screen_x, screen_y, self.TILE_SIZE, self.TILE_SIZE)

        # Animated wave effect for time-based animations
        wave = math.sin(self.time * 2 + grid_x * 0.5 + grid_y * 0.5) * 0.5 + 0.5

        # Base ground with subtle checkerboard
        if (grid_x + grid_y) % 2 == 0:
            color = self.color_empty1
        else:
            color = self.color_empty2
        pygame.draw.rect(self.screen, color, rect)

        # Lava with animated glow
        if cell.startswith('L'):
            # Base lava
            lava_color = (
                int(self.color_lava[0] - wave * 30),
                int(self.color_lava[1] + wave * 20),
                int(self.color_lava[2])
            )
            pygame.draw.rect(self.screen, lava_color, rect)
            
            # Animated lava bubbles
            bubble_offset = int(wave * 5)
            bubble_size = 4 + int(wave * 2)
            bubble_x = screen_x + self.TILE_SIZE // 2 + int(math.cos(self.time * 3 + grid_x) * 8)
            bubble_y = screen_y + self.TILE_SIZE // 2 + int(math.sin(self.time * 3 + grid_y) * 8)
            
            # Glow effect
            glow_surface = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
            glow_color = (*self.color_lava_dark, int(100 + wave * 50))
            pygame.draw.circle(glow_surface, glow_color, (self.TILE_SIZE // 2, self.TILE_SIZE // 2), self.TILE_SIZE // 2)
            self.screen.blit(glow_surface, (screen_x, screen_y))
            
            # Bubble highlight
            pygame.draw.circle(self.screen, (255, 150, 50, 150), (bubble_x, bubble_y), bubble_size)

        # Aqua with wave animation
        if cell.startswith('A'):
            # Base aqua
            aqua_color = (
                int(self.color_aqua[0] + wave * 20),
                int(self.color_aqua[1] + wave * 30),
                int(self.color_aqua[2])
            )
            pygame.draw.rect(self.screen, aqua_color, rect)
            
            # Wave lines
            wave_y = int(wave * 4)
            for i in range(3):
                y_pos = screen_y + 10 + i * 12 + wave_y
                wave_x_offset = int(math.sin(self.time * 2 + i + grid_x * 0.3) * 3)
                pygame.draw.line(self.screen, self.color_aqua_dark, 
                               (screen_x + 5 + wave_x_offset, y_pos), 
                               (screen_x + self.TILE_SIZE - 5 + wave_x_offset, y_pos), 2)

        # Solid wall with 3D effect
        if cell == 'W':
            # Shadow
            shadow_rect = rect.inflate(-4, -4).move(2, 2)
            pygame.draw.rect(self.screen, (40, 45, 60), shadow_rect, border_radius=4)
            
            # Main wall
            wall_rect = rect.inflate(-4, -4)
            pygame.draw.rect(self.screen, self.color_wall, wall_rect, border_radius=4)
            
            # Highlight
            highlight = wall_rect.copy()
            highlight.height = highlight.height // 3
            pygame.draw.rect(self.screen, (90, 95, 110), highlight, border_radius=4)

        # Pass-through wall with pulsing corners
        if cell.endswith('P'):
            corner_size = 8
            pulse = int(wave * 20)
            corner_color = (100 + pulse, 100 + pulse, 140 + pulse)
            
            corners = [
                (screen_x + 4, screen_y + 4),
                (screen_x + self.TILE_SIZE - corner_size - 4, screen_y + 4),
                (screen_x + 4, screen_y + self.TILE_SIZE - corner_size - 4),
                (screen_x + self.TILE_SIZE - corner_size - 4, screen_y + self.TILE_SIZE - corner_size - 4)
            ]
            
            for cx, cy in corners:
                corner_rect = pygame.Rect(cx, cy, corner_size, corner_size)
                pygame.draw.rect(self.screen, corner_color, corner_rect, border_radius=2)
                pygame.draw.rect(self.screen, (120, 120, 160), corner_rect, 1, border_radius=2)

        # Numbered wall with glowing number
        if cell.startswith('C'):
            # Shadow
            shadow_rect = rect.inflate(-4, -4).move(2, 2)
            pygame.draw.rect(self.screen, (40, 45, 60), shadow_rect, border_radius=4)
            
            # Main wall
            wall_rect = rect.inflate(-4, -4)
            pygame.draw.rect(self.screen, self.color_wall, wall_rect, border_radius=4)
            
            # Number with glow
            str_num = cell[1:]
            glow_alpha = int(150 + wave * 100)
            
            # Render glow
            for offset in [(0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]:
                glow_text = self.font_wall.render(str_num, True, (100, 200, 255))
                glow_text.set_alpha(glow_alpha // 3)
                glow_rect = glow_text.get_rect(center=(rect.centerx + offset[0], rect.centery + offset[1]))
                self.screen.blit(glow_text, glow_rect)
            
            # Main number
            count_text = self.font_wall.render(str_num, True, (255, 255, 255))
            text_rect = count_text.get_rect(center=rect.center)
            self.screen.blit(count_text, text_rect)

        # Stone box with 3D appearance
        if cell == 'S':
            # Shadow
            shadow_rect = rect.inflate(-6, -6).move(3, 3)
            pygame.draw.rect(self.screen, self.color_stone_shadow, shadow_rect, border_radius=3)
            
            # Main stone
            stone_rect = rect.inflate(-6, -6)
            pygame.draw.rect(self.screen, self.color_stone, stone_rect, border_radius=3)
            
            # Highlight
            highlight_rect = stone_rect.copy()
            highlight_rect.height = highlight_rect.height // 2
            pygame.draw.rect(self.screen, (170, 175, 180), highlight_rect, border_radius=3)
            
            # Corner rivets
            rivet_size = 4
            rivet_color = (80, 85, 90)
            rivets = [
                (stone_rect.left + 6, stone_rect.top + 6),
                (stone_rect.right - 6, stone_rect.top + 6),
                (stone_rect.left + 6, stone_rect.bottom - 6),
                (stone_rect.right - 6, stone_rect.bottom - 6)
            ]
            for rx, ry in rivets:
                pygame.draw.circle(self.screen, rivet_color, (rx, ry), rivet_size)
                pygame.draw.circle(self.screen, (120, 125, 130), (rx - 1, ry - 1), rivet_size // 2)

        # Animated golden key
        if pos in board.keys:
            key_pulse = math.sin(self.time * 4) * 0.15 + 1
            key_radius = int(10 * key_pulse)
            key_center = (screen_x + self.TILE_SIZE // 2, screen_y + self.TILE_SIZE // 2 - 5)
            
            # Glow
            glow_surf = pygame.Surface((key_radius * 4, key_radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color_key, 80), (key_radius * 2, key_radius * 2), key_radius * 2)
            self.screen.blit(glow_surf, (key_center[0] - key_radius * 2, key_center[1] - key_radius * 2))
            
            # Key body
            pygame.draw.circle(self.screen, self.color_key, key_center, key_radius)
            pygame.draw.circle(self.screen, (255, 235, 100), key_center, key_radius, 2)
            
            # Shine
            shine_pos = (key_center[0] - 3, key_center[1] - 3)
            pygame.draw.circle(self.screen, (255, 255, 200), shine_pos, 3)

        # Magical gate with particles
        if pos == board.gate_pos:
            gate_pulse = math.sin(self.time * 3) * 0.1 + 1
            gate_size = int(30 * gate_pulse)
            gate_rect = pygame.Rect(screen_x + (self.TILE_SIZE - gate_size) // 2,
                                   screen_y + (self.TILE_SIZE - gate_size) // 2,
                                   gate_size, gate_size)
            
            # Outer glow
            glow_surf = pygame.Surface((gate_size * 2, gate_size * 2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.color_gate, 60), 
                           (gate_size // 2, gate_size // 2, gate_size, gate_size), 
                           border_radius=5)
            self.screen.blit(glow_surf, (gate_rect.x - gate_size // 2, gate_rect.y - gate_size // 2))
            
            # Gate frame
            pygame.draw.rect(self.screen, self.color_gate, gate_rect, 4, border_radius=4)
            
            # Inner frame with rotation effect
            inner_rect = gate_rect.inflate(-10, -10)
            rotation_offset = int(math.sin(self.time * 2) * 2)
            inner_rect = inner_rect.move(rotation_offset, -rotation_offset)
            pygame.draw.rect(self.screen, (180, 100, 255), inner_rect, 3, border_radius=3)
            
            # Center sparkle
            sparkle_alpha = int(200 + math.sin(self.time * 5) * 55)
            sparkle_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(sparkle_surf, (255, 255, 255, sparkle_alpha), (5, 5), 5)
            self.screen.blit(sparkle_surf, (gate_rect.centerx - 5, gate_rect.centery - 5))

        # Animated player
        if board.player.position == pos:
            if self.player_sprite:
                # Update target position
                target_x = screen_x + self.TILE_SIZE // 2
                target_y = screen_y + self.TILE_SIZE // 2
                self.player_sprite.set_target(target_x, target_y)
                
                player_x, player_y = self.player_sprite.get_pos()
            else:
                player_x = screen_x + self.TILE_SIZE // 2
                player_y = screen_y + self.TILE_SIZE // 2
            
            # Bobbing animation
            bob = math.sin(self.time * 4) * 2
            player_y += int(bob)
            
            
            player_radius = 16
            
            # Shadow
            shadow_surf = pygame.Surface((player_radius * 3, player_radius // 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect())
            self.screen.blit(shadow_surf, (player_x - player_radius * 1.5, screen_y + self.TILE_SIZE - player_radius // 2 - 5))
            
            # Glow
            glow_surf = pygame.Surface((player_radius * 3, player_radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color_player, 60), 
                             (player_radius * 1.5, player_radius * 1.5), player_radius * 1.5)
            self.screen.blit(glow_surf, (player_x - player_radius * 1.5, player_y - player_radius * 1.5))
            
            # Player body with gradient
            pygame.draw.circle(self.screen, self.color_player, (player_x, player_y), player_radius)
            pygame.draw.circle(self.screen, (255, 200, 100), (player_x, player_y), player_radius, 2)
            
            # Highlight
            highlight_pos = (player_x - 5, player_y - 5)
            pygame.draw.circle(self.screen, (255, 230, 150), highlight_pos, 6)
            
            # Animated eyes
            eye_color = (40, 40, 40)
            eye_radius = 3
            blink = 1.0
            if math.sin(self.time * 3) > 0.95:
                blink = 0.3
            
            left_eye = (player_x - 6, int(player_y - 3 + bob * 0.3))
            right_eye = (player_x + 6, int(player_y - 3 + bob * 0.3))
            
            eye_height = int(eye_radius * 2 * blink)
            if eye_height > 0:
                pygame.draw.ellipse(self.screen, eye_color, 
                                  (left_eye[0] - eye_radius, left_eye[1] - eye_height // 2, 
                                   eye_radius * 2, eye_height))
                pygame.draw.ellipse(self.screen, eye_color, 
                                  (right_eye[0] - eye_radius, right_eye[1] - eye_height // 2, 
                                   eye_radius * 2, eye_height))

        # Subtle grid border
        pygame.draw.rect(self.screen, (200, 200, 210, 100), rect, 1)

    def _render_hud(self, move_count):
        """Render HUD with modern styling"""
        # Semi-transparent background bar
        hud_height = 50
        hud_surface = pygame.Surface((self.screen.get_width(), hud_height), pygame.SRCALPHA)
        pygame.draw.rect(hud_surface, (20, 23, 30, 220), hud_surface.get_rect(), border_radius=0)
        self.screen.blit(hud_surface, (0, 0))
        
        # Move counter with icon
        moves_text = f"Moves: {move_count}"
        text_surface = self.font_hud.render(moves_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (30, 12))
        
        # Instructions on the right
        instructions = "ESC: Menu  |  R: Restart"
        inst_surface = self.font_small.render(instructions, True, (180, 180, 200))
        inst_rect = inst_surface.get_rect(right=self.screen.get_width() - 30, centery=25)
        self.screen.blit(inst_surface, inst_rect)
        
    
    def _render_statistics_panel(self, ai_time, explored_states, generated_states, path_length, game_status, board_x, board_width):
        """Render beautiful statistics panel on the right side"""
        # Panel dimensions
        panel_width = 280
        panel_x = board_x + board_width + 30
        panel_y = 100
        
        # If panel would go off screen, put it on the left
        if panel_x + panel_width > self.screen.get_width() - 20:
            panel_x = board_x - panel_width - 30
        
        # Status indicator color based on game state
        if game_status == "win":
            status_color = (100, 255, 100)
            status_glow = (50, 200, 50)
            status_text = "VICTORY!"
        elif game_status == "death":
            status_color = (255, 100, 100)
            status_glow = (200, 50, 50)
            status_text = "GAME OVER"
        else:
            status_color = (100, 180, 255)
            status_glow = (50, 120, 200)
            status_text = "IN PROGRESS"
        
        # Panel background with shadow
        shadow_surf = pygame.Surface((panel_width + 10, 450), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect(), border_radius=15)
        self.screen.blit(shadow_surf, (panel_x - 5, panel_y - 5))
        
        # Main panel background with gradient
        panel_surf = pygame.Surface((panel_width, 440), pygame.SRCALPHA)
        for i in range(440):
            alpha = 200 - int(i / 440 * 20)
            color = (25 + i // 20, 28 + i // 20, 40 + i // 15, alpha)
            pygame.draw.rect(panel_surf, color, (0, i, panel_width, 1))
        
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        # Panel border with glow
        glow_intensity = int(50 + math.sin(self.time * 2) * 30)
        pygame.draw.rect(self.screen, (*status_glow, glow_intensity), 
                        (panel_x - 2, panel_y - 2, panel_width + 4, 444), 3, border_radius=15)
        pygame.draw.rect(self.screen, (80, 90, 120), 
                        (panel_x, panel_y, panel_width, 440), 2, border_radius=15)
        
        # Title
        title_y = panel_y + 20
        title_surf = self.font_hud.render("STATISTICS", True, (255, 255, 255))
        title_rect = title_surf.get_rect(centerx=panel_x + panel_width // 2, y=title_y)
        
        # Title glow
        title_glow = self.font_hud.render("STATISTICS", True, (100, 150, 255))
        title_glow.set_alpha(100)
        for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            glow_rect = title_rect.copy()
            glow_rect.x += dx * 2
            glow_rect.y += dy * 2
            self.screen.blit(title_glow, glow_rect)
        
        self.screen.blit(title_surf, title_rect)
        
        # Status badge
        status_y = panel_y + 70
        badge_width = panel_width - 40
        badge_height = 50
        badge_rect = pygame.Rect(panel_x + 20, status_y, badge_width, badge_height)
        
        # Animated pulse for status
        pulse = math.sin(self.time * 3) * 0.1 + 1
        pulse_rect = badge_rect.inflate(int(5 * pulse), int(3 * pulse))
        
        # Status glow
        glow_surf = pygame.Surface((pulse_rect.width + 20, pulse_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*status_color, 60), glow_surf.get_rect(), border_radius=10)
        self.screen.blit(glow_surf, (pulse_rect.x - 10, pulse_rect.y - 10))
        
        # Status background
        pygame.draw.rect(self.screen, (*status_color, 150), pulse_rect, border_radius=8)
        pygame.draw.rect(self.screen, status_color, pulse_rect, 3, border_radius=8)
        
        # Status text
        status_surf = self.font_wall.render(status_text, True, (255, 255, 255))
        status_rect = status_surf.get_rect(center=pulse_rect.center)
        
        # Text shadow
        shadow_surf = self.font_wall.render(status_text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(pulse_rect.centerx + 2, pulse_rect.centery + 2))
        self.screen.blit(shadow_surf, shadow_rect)
        self.screen.blit(status_surf, status_rect)
        
        # Statistics items
        stats_y = status_y + 80
        line_height = 75
        
        # Format AI time as HH:MM:SS
        hours = int(ai_time // 3600)
        minutes = int((ai_time % 3600) // 60)
        seconds = int(ai_time % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        stats = [
            ("AI Time", time_str, (255, 200, 100)),
            ("Explored", f"{explored_states:,}", (100, 200, 255)),
            ("Generated", f"{generated_states:,}", (255, 150, 255)),
            ("Path Length", str(path_length), (150, 255, 150))
        ]
        
        for i, (label, value, color) in enumerate(stats):
            item_y = stats_y + i * line_height
            
            # Item container
            item_rect = pygame.Rect(panel_x + 15, item_y, panel_width - 30, 65)
            
            # Subtle hover effect based on time
            wave_offset = math.sin(self.time * 2 + i * 0.5) * 2
            item_rect.y += int(wave_offset)
            
            # Background
            bg_alpha = 80 + int(math.sin(self.time + i) * 20)
            pygame.draw.rect(self.screen, (40, 45, 60, bg_alpha), item_rect, border_radius=8)
            pygame.draw.rect(self.screen, (70, 80, 100), item_rect, 1, border_radius=8)
            
            # Label
            label_surf = self.font_small.render(label, True, (180, 190, 210))
            label_rect = label_surf.get_rect(topleft=(item_rect.x + 15, item_rect.y + 10))
            self.screen.blit(label_surf, label_rect)
            
            # Value with glow
            value_surf = self.font_hud.render(value, True, color)
            value_rect = value_surf.get_rect(topleft=(item_rect.x + 15, item_rect.y + 32))
            
            # Value glow
            glow_value = self.font_hud.render(value, True, color)
            glow_alpha = int(80 + math.sin(self.time * 2 + i) * 40)
            glow_value.set_alpha(glow_alpha)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                glow_rect = value_rect.copy()
                glow_rect.x += dx
                glow_rect.y += dy
                self.screen.blit(glow_value, glow_rect)
            
            self.screen.blit(value_surf, value_rect)
            
            # Icon/indicator dot
            dot_radius = 4
            dot_x = item_rect.right - 15
            dot_y = item_rect.centery
            dot_pulse = 1 + math.sin(self.time * 3 + i * 0.8) * 0.3
            pygame.draw.circle(self.screen, color, (dot_x, dot_y), int(dot_radius * dot_pulse))
            pygame.draw.circle(self.screen, (255, 255, 255), (dot_x, dot_y), int(dot_radius * dot_pulse), 1)