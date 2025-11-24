"""
Dialog View - Modal dialogs for win/death
"""

import pygame


class DialogView:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 64)
        self.font_message = pygame.font.Font(None, 40)
        self.font_button = pygame.font.Font(None, 36)
        
        self.restart_button = pygame.Rect(0, 0, 180, 50)
        self.quit_button = pygame.Rect(0, 0, 180, 50)
    
    def handle_event(self, event, title, message):
        """Handle dialog events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.restart_button.collidepoint(mouse_pos):
                return "restart"
            elif self.quit_button.collidepoint(mouse_pos):
                return "quit"
        
        return None
    
    def render(self, title, message):
        """Render dialog box"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_width = 500
        dialog_height = 300
        dialog_rect = pygame.Rect(0, 0, dialog_width, dialog_height)
        dialog_rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2)
        
        pygame.draw.rect(self.screen, (60, 60, 80), dialog_rect, border_radius=15)
        pygame.draw.rect(self.screen, (200, 200, 200), dialog_rect, 3, border_radius=15)
        
        # Title
        title_color = (100, 255, 100) if "Victory" in title else (255, 100, 100)
        title_surface = self.font_title.render(title, True, title_color)
        title_rect = title_surface.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 60))
        self.screen.blit(title_surface, title_rect)
        
        # Message
        message_surface = self.font_message.render(message, True, (255, 255, 255))
        message_rect = message_surface.get_rect(center=(dialog_rect.centerx, dialog_rect.centery))
        self.screen.blit(message_surface, message_rect)
        
        # Buttons
        button_y = dialog_rect.bottom - 70
        button_spacing = 40
        
        self.restart_button.center = (dialog_rect.centerx - 100, button_y)
        self.quit_button.center = (dialog_rect.centerx + 100, button_y)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Restart button
        restart_hover = self.restart_button.collidepoint(mouse_pos)
        restart_color = (100, 200, 100) if restart_hover else (70, 150, 70)
        pygame.draw.rect(self.screen, restart_color, self.restart_button, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), self.restart_button, 2, border_radius=8)
        
        restart_text = self.font_button.render("Restart", True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=self.restart_button.center)
        self.screen.blit(restart_text, restart_text_rect)
        
        # Quit button
        quit_hover = self.quit_button.collidepoint(mouse_pos)
        quit_color = (200, 100, 100) if quit_hover else (150, 70, 70)
        pygame.draw.rect(self.screen, quit_color, self.quit_button, border_radius=8)
        pygame.draw.rect(self.screen, (255, 255, 255), self.quit_button, 2, border_radius=8)
        
        quit_text = self.font_button.render("Menu", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=self.quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)