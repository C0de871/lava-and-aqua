"""
Menu View - Enhanced with beautiful animations and modern design
"""

import pygame
import math
import random


class FloatingParticle:
    """Background floating particles for ambiance"""
    def __init__(self, screen_width, screen_height):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-1, -0.3)
        self.color = random.choice([
            (100, 150, 255),
            (255, 150, 100),
            (150, 255, 200),
            (255, 200, 150)
        ])
        self.alpha = random.randint(100, 200)
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def update(self, dt):
        self.x += self.speed_x * dt * 60
        self.y += self.speed_y * dt * 60
        
        # Wrap around
        if self.y < 0:
            self.y = self.screen_height
            self.x = random.randint(0, self.screen_width)
        if self.x < 0:
            self.x = self.screen_width
        if self.x > self.screen_width:
            self.x = 0
    
    def render(self, screen):
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, self.alpha), (self.size, self.size), self.size)
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))


class AnimatedButton:
    """Button with hover animations"""
    def __init__(self, rect, label, color, hover_color):
        self.rect = rect
        self.label = label
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.scale = 1.0
        self.target_scale = 1.0
        self.glow_intensity = 0
        self.hover_time = 0
    
    def update(self, dt, is_hover):
        # Smooth scale transition
        self.target_scale = 1.08 if is_hover else 1.0
        scale_diff = self.target_scale - self.scale
        self.scale += scale_diff * 8 * dt
        
        # Color transition
        if is_hover:
            self.hover_time += dt
            # Interpolate toward hover color
            for i in range(3):
                diff = self.hover_color[i] - self.current_color[i]
                self.current_color = tuple(
                    int(self.current_color[j] + (self.hover_color[j] - self.current_color[j]) * 8 * dt)
                    if j == i else self.current_color[j]
                    for j in range(3)
                )
            self.glow_intensity = min(1.0, self.glow_intensity + dt * 4)
        else:
            self.hover_time = 0
            # Interpolate toward base color
            for i in range(3):
                diff = self.color[i] - self.current_color[i]
                self.current_color = tuple(
                    int(self.current_color[j] + (self.color[j] - self.current_color[j]) * 8 * dt)
                    if j == i else self.current_color[j]
                    for j in range(3)
                )
            self.glow_intensity = max(0, self.glow_intensity - dt * 4)
    
    def render(self, screen, font):
        # Calculate scaled rect
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_width // 2,
            self.rect.centery - scaled_height // 2,
            scaled_width,
            scaled_height
        )
        
        # Glow effect
        if self.glow_intensity > 0:
            glow_size = int(10 * self.glow_intensity)
            glow_rect = scaled_rect.inflate(glow_size * 2, glow_size * 2)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            alpha = int(100 * self.glow_intensity)
            pygame.draw.rect(glow_surf, (*self.current_color, alpha), 
                           glow_surf.get_rect(), border_radius=15)
            screen.blit(glow_surf, glow_rect.topleft)
        
        # Button background with gradient effect
        pygame.draw.rect(screen, self.current_color, scaled_rect, border_radius=12)
        
        # Highlight at top
        highlight_rect = scaled_rect.copy()
        highlight_rect.height = highlight_rect.height // 3
        highlight_color = tuple(min(255, c + 30) for c in self.current_color)
        pygame.draw.rect(screen, highlight_color, highlight_rect, border_radius=12)
        
        # Border
        border_color = tuple(min(255, c + 40) for c in self.current_color)
        pygame.draw.rect(screen, border_color, scaled_rect, 3, border_radius=12)
        
        # Animated shine effect on hover
        if self.glow_intensity > 0:
            shine_offset = int(math.sin(self.hover_time * 3) * 10)
            shine_rect = pygame.Rect(
                scaled_rect.left + scaled_rect.width // 4 + shine_offset,
                scaled_rect.top + 5,
                scaled_rect.width // 4,
                scaled_rect.height - 10
            )
            shine_surf = pygame.Surface((shine_rect.width, shine_rect.height), pygame.SRCALPHA)
            alpha = int(50 * self.glow_intensity)
            pygame.draw.rect(shine_surf, (255, 255, 255, alpha), shine_surf.get_rect(), border_radius=8)
            screen.blit(shine_surf, shine_rect.topleft)
        
        # Text
        text = font.render(self.label, True, (255, 255, 255))
        text_rect = text.get_rect(center=scaled_rect.center)
        
        # Text shadow
        shadow = font.render(self.label, True, (0, 0, 0, 180))
        shadow_rect = shadow.get_rect(center=(scaled_rect.centerx + 2, scaled_rect.centery + 2))
        screen.blit(shadow, shadow_rect)
        
        screen.blit(text, text_rect)


class MenuView:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 96)
        self.font_subtitle = pygame.font.Font(None, 36)
        self.font_button = pygame.font.Font(None, 48)
        
        # Animation state
        self.time = 0
        self.title_offset = -100
        self.title_alpha = 0
        
        # Background particles
        self.particles = [
            FloatingParticle(screen.get_width(), screen.get_height())
            for _ in range(50)
        ]
        
        # Animated buttons
        center_x = self.screen.get_width() // 2
        start_y = 300
        spacing = 90
        
        self.animated_buttons = {
            "human": AnimatedButton(
                pygame.Rect(center_x - 150, start_y, 300, 70),
                "Play as Human",
                (70, 120, 200),
                (90, 150, 240)
            ),
            "ai": AnimatedButton(
                pygame.Rect(center_x - 150, start_y + spacing, 300, 70),
                "Watch AI Play",
                (200, 70, 120),
                (240, 90, 150)
            ),
            "quit": AnimatedButton(
                pygame.Rect(center_x - 150, start_y + spacing * 2, 300, 70),
                "Quit",
                (120, 70, 70),
                (150, 90, 90)
            )
        }
        
        # Store rects for collision detection
        self.buttons = {
            action: btn.rect for action, btn in self.animated_buttons.items()
        }

    def update(self, dt):
        """Update animations"""
        self.time += dt
        
        # Title entrance animation
        if self.title_offset < 0:
            self.title_offset += dt * 200
            self.title_offset = min(0, self.title_offset)
        
        if self.title_alpha < 255:
            self.title_alpha += dt * 300
            self.title_alpha = min(255, self.title_alpha)
        
        # Update particles
        for particle in self.particles:
            particle.update(dt)
        
        # Update buttons
        mouse_pos = pygame.mouse.get_pos()
        for action, btn in self.animated_buttons.items():
            is_hover = btn.rect.collidepoint(mouse_pos)
            btn.update(dt, is_hover)

    def handle_event(self, event):
        """Handle menu events, return action if button clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for action, btn in self.animated_buttons.items():
                if btn.rect.collidepoint(mouse_pos):
                    return action
        return None

    def render(self):
        """Render the menu with animations"""
        # Animated gradient background
        wave1 = math.sin(self.time * 0.5) * 10
        wave2 = math.cos(self.time * 0.7) * 10
        
        for y in range(0, self.screen.get_height(), 4):
            progress = y / self.screen.get_height()
            color = (
                int(20 + progress * 20 + wave1),
                int(25 + progress * 25 + wave2),
                int(40 + progress * 30)
            )
            pygame.draw.rect(self.screen, color, (0, y, self.screen.get_width(), 4))
        
        # Render floating particles
        for particle in self.particles:
            particle.render(self.screen)
        
        # Animated title with glow
        title_y = 120 + int(self.title_offset)
        
        # Title glow
        glow_offset = int(math.sin(self.time * 2) * 3)
        for offset in range(5, 0, -1):
            glow_alpha = int((self.title_alpha // 3) * (1 - offset / 6))
            title_glow = self.font_title.render("Lava & Aqua", True, (100, 150, 255))
            title_glow.set_alpha(glow_alpha)
            glow_rect = title_glow.get_rect(center=(
                self.screen.get_width() // 2 + glow_offset,
                title_y + glow_offset
            ))
            for dx, dy in [(-offset, -offset), (offset, -offset), (-offset, offset), (offset, offset)]:
                gr = glow_rect.copy()
                gr.x += dx
                gr.y += dy
                self.screen.blit(title_glow, gr)
        
        # Main title with gradient effect
        title_surf = pygame.Surface((600, 120), pygame.SRCALPHA)
        
        # Create gradient text effect
        title_text = "Lava & Aqua"
        for i, char in enumerate(title_text):
            char_offset = math.sin(self.time * 2 + i * 0.5) * 5
            color_shift = int(math.sin(self.time + i * 0.3) * 30)
            char_color = (
                255,
                200 + color_shift,
                100 + color_shift
            )
            char_surf = self.font_title.render(char, True, char_color)
            char_surf.set_alpha(int(self.title_alpha))
            
            # Calculate position for this character
            temp_surf = self.font_title.render(title_text[:i], True, (255, 255, 255))
            char_x = temp_surf.get_width()
            title_surf.blit(char_surf, (char_x, int(char_offset)))
        
        title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2, title_y))
        self.screen.blit(title_surf, title_rect)
        
        # Subtitle with fade-in
        if self.title_alpha > 100:
            subtitle = "A Puzzle Adventure"
            subtitle_alpha = min(255, self.title_alpha - 100)
            subtitle_surf = self.font_subtitle.render(subtitle, True, (180, 180, 220))
            subtitle_surf.set_alpha(subtitle_alpha)
            subtitle_rect = subtitle_surf.get_rect(center=(self.screen.get_width() // 2, title_y + 60))
            self.screen.blit(subtitle_surf, subtitle_rect)
        
        # Render animated buttons
        for action, btn in self.animated_buttons.items():
            btn.render(self.screen, self.font_button)
        
        # Footer with version or credits
        footer_alpha = min(255, int(self.title_alpha))
        footer = self.font_subtitle.render("Use arrow keys or WASD to move", True, (120, 120, 150))
        footer.set_alpha(footer_alpha)
        footer_rect = footer.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 40))
        self.screen.blit(footer, footer_rect)