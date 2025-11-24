"""
Menu View - Main menu screen
"""

import pygame


class MenuView:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 48)

        # Button definitions
        self.buttons = {
            "human": pygame.Rect(0, 0, 300, 60),
            "ai": pygame.Rect(0, 0, 300, 60),
            "quit": pygame.Rect(0, 0, 300, 60)
        }

        self._position_buttons()

    def _position_buttons(self):
        """Center buttons on screen"""
        center_x = self.screen.get_width() // 2
        start_y = 300
        spacing = 80

        self.buttons["human"].center = (center_x, start_y)
        self.buttons["ai"].center = (center_x, start_y + spacing)
        self.buttons["quit"].center = (center_x, start_y + spacing * 2)

    def handle_event(self, event):
        """Handle menu events, return action if button clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for action, rect in self.buttons.items():
                if rect.collidepoint(mouse_pos):
                    return action
        return None

    def render(self):
        """Render the menu"""
        # Background
        self.screen.fill((40, 40, 60))

        # Title
        title = self.font_title.render("Lava & Aqua", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title, title_rect)

        # Buttons
        mouse_pos = pygame.mouse.get_pos()

        button_labels = {
            "human": "Play as Human",
            "ai": "Watch AI Play",
            "quit": "Quit"
        }

        for action, rect in self.buttons.items():
            # Check if mouse is hovering
            is_hover = rect.collidepoint(mouse_pos)
            color = (100, 150, 255) if is_hover else (70, 100, 180)

            # Draw button
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255),
                             rect, 2, border_radius=10)

            # Draw text
            text = self.font_button.render(
                button_labels[action], True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
