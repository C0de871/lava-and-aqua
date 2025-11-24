"""
File Chooser View - Simple file browser for board files
"""

import pygame
import os


class FileChooserView:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 48)
        self.font_item = pygame.font.Font(None, 32)
        
        self.current_path = os.path.join(os.getcwd(), "boards")
        if not os.path.exists(self.current_path):
            os.makedirs(self.current_path)
        
        self.files = []
        self.scroll_offset = 0
        self.selected_index = -1
        
        self.back_button = pygame.Rect(50, 50, 100, 40)
        self.select_button = pygame.Rect(0, 0, 150, 50)
        self.select_button.center = (self.screen.get_width() // 2, self.screen.get_height() - 80)
        
        self._load_files()
    
    def _load_files(self):
        """Load .txt files from boards directory"""
        self.files = []
        if os.path.exists(self.current_path):
            for f in os.listdir(self.current_path):
                if f.endswith('.txt'):
                    self.files.append(f)

        # Extract the number after "level " and sort numerically
        self.files.sort(key=lambda x: int(x.replace("level", "").replace(".txt", "").strip()))


    
    def handle_event(self, event):
        """Handle file chooser events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Back button
            if self.back_button.collidepoint(mouse_pos):
                return "back"
            
            # Select button
            if self.select_button.collidepoint(mouse_pos) and self.selected_index >= 0:
                filepath = os.path.join(self.current_path, self.files[self.selected_index])
                return f"file:{filepath}"
            
            # File items
            start_y = 150
            item_height = 40
            spacing = 10
            
            for i, filename in enumerate(self.files):
                y = start_y + i * (item_height + spacing) - self.scroll_offset
                rect = pygame.Rect(100, y, self.screen.get_width() - 200, item_height)
                
                if rect.collidepoint(mouse_pos) and 100 < y < self.screen.get_height() - 150:
                    self.selected_index = i
                    break
        
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 30
            self.scroll_offset = max(0, self.scroll_offset)
        
        return None
    
    def render(self):
        """Render file chooser"""
        self.screen.fill((40, 40, 60))
        
        # Title
        title = self.font_title.render("Select Board File", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.back_button.collidepoint(mouse_pos)
        color = (100, 100, 100) if is_hover else (70, 70, 70)
        pygame.draw.rect(self.screen, color, self.back_button, border_radius=5)
        pygame.draw.rect(self.screen, (255, 255, 255), self.back_button, 2, border_radius=5)
        
        back_text = self.font_item.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)
        
        # File list
        if not self.files:
            no_files = self.font_item.render("No board files found in 'boards/' directory", True, (200, 200, 200))
            no_files_rect = no_files.get_rect(center=(self.screen.get_width() // 2, 300))
            self.screen.blit(no_files, no_files_rect)
        else:
            start_y = 150
            item_height = 40
            spacing = 10
            
            # Create clipping area for file list
            clip_rect = pygame.Rect(100, 150, self.screen.get_width() - 200, self.screen.get_height() - 300)
            
            for i, filename in enumerate(self.files):
                y = start_y + i * (item_height + spacing) - self.scroll_offset
                
                if y < 100 or y > self.screen.get_height() - 150:
                    continue
                
                rect = pygame.Rect(100, y, self.screen.get_width() - 200, item_height)
                
                # Highlight selected
                is_selected = (i == self.selected_index)
                is_hover = rect.collidepoint(mouse_pos) and clip_rect.collidepoint(mouse_pos)
                
                if is_selected:
                    color = (80, 120, 200)
                elif is_hover:
                    color = (60, 80, 120)
                else:
                    color = (50, 50, 70)
                
                pygame.draw.rect(self.screen, color, rect, border_radius=5)
                pygame.draw.rect(self.screen, (100, 100, 100), rect, 1, border_radius=5)
                
                # File name
                text = self.font_item.render(filename, True, (255, 255, 255))
                text_rect = text.get_rect(midleft=(rect.left + 10, rect.centery))
                self.screen.blit(text, text_rect)
        
        # Select button
        if self.selected_index >= 0:
            is_hover = self.select_button.collidepoint(mouse_pos)
            color = (100, 200, 100) if is_hover else (70, 150, 70)
            pygame.draw.rect(self.screen, color, self.select_button, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), self.select_button, 2, border_radius=10)
            
            select_text = self.font_item.render("Load Board", True, (255, 255, 255))
            select_rect = select_text.get_rect(center=self.select_button.center)
            self.screen.blit(select_text, select_rect)