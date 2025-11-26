"""
File Chooser View - Enhanced with smooth animations and modern design
"""

import pygame
import os
import math


class FileItem:
    """Animated file list item"""
    def __init__(self, filename, index, y_pos):
        self.filename = filename
        self.index = index
        self.target_y = y_pos
        self.current_y = y_pos
        self.alpha = 0
        self.target_alpha = 255
        self.scale = 0.8
        self.target_scale = 1.0
        self.hover_intensity = 0
        self.select_intensity = 0
    
    def update(self, dt, target_y, is_hover, is_selected):
        # Smooth position transition
        self.target_y = target_y
        y_diff = self.target_y - self.current_y
        self.current_y += y_diff * 10 * dt
        
        # Fade in animation
        alpha_diff = self.target_alpha - self.alpha
        self.alpha += alpha_diff * 8 * dt
        
        # Scale animation
        scale_diff = self.target_scale - self.scale
        self.scale += scale_diff * 8 * dt
        
        # Hover animation
        if is_hover:
            self.hover_intensity = min(1.0, self.hover_intensity + dt * 6)
        else:
            self.hover_intensity = max(0, self.hover_intensity - dt * 6)
        
        # Selection animation
        if is_selected:
            self.select_intensity = min(1.0, self.select_intensity + dt * 8)
        else:
            self.select_intensity = max(0, self.select_intensity - dt * 8)


class FileChooserView:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 64)
        self.font_item = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        self.current_path = os.path.join(os.getcwd(), "boards")
        if not os.path.exists(self.current_path):
            os.makedirs(self.current_path)
        
        self.files = []
        self.file_items = []
        self.scroll_offset = 0
        self.target_scroll = 0
        self.selected_index = -1
        
        # Animation state
        self.time = 0
        self.title_wave = 0
        
        # Button animations
        self.back_button = pygame.Rect(40, 40, 120, 50)
        self.back_hover = 0
        
        self.select_button = pygame.Rect(0, 0, 180, 60)
        self.select_button.center = (self.screen.get_width() // 2, self.screen.get_height() - 80)
        self.select_hover = 0
        self.select_pulse = 0
        
        self._load_files()
    
    def _load_files(self):
        """Load .txt files from boards directory"""
        self.files = []
        if os.path.exists(self.current_path):
            for f in os.listdir(self.current_path):
                if f.endswith('.txt'):
                    self.files.append(f)
        
        # Sort files numerically
        self.files.sort(key=lambda x: int(x.replace("level", "").replace(".txt", "").strip()) 
                       if x.replace("level", "").replace(".txt", "").strip().isdigit() else 999)
        
        # Create file items with staggered animation
        start_y = 180
        item_height = 50
        spacing = 12
        
        self.file_items = []
        for i, filename in enumerate(self.files):
            y = start_y + i * (item_height + spacing)
            item = FileItem(filename, i, y)
            # Stagger the entrance animation
            item.alpha = 0
            item.scale = 0.5
            self.file_items.append(item)
    
    def update(self, dt):
        """Update animations"""
        self.time += dt
        
        # Smooth scroll
        scroll_diff = self.target_scroll - self.scroll_offset
        self.scroll_offset += scroll_diff * 10 * dt
        
        # Update file items
        start_y = 180
        item_height = 50
        spacing = 12
        mouse_pos = pygame.mouse.get_pos()
        
        for i, item in enumerate(self.file_items):
            y = start_y + i * (item_height + spacing) - self.scroll_offset
            rect = pygame.Rect(80, y, self.screen.get_width() - 160, item_height)
            
            is_hover = rect.collidepoint(mouse_pos) and 150 < y < self.screen.get_height() - 150
            is_selected = (i == self.selected_index)
            
            # Staggered entrance
            if self.time > i * 0.05:
                item.target_alpha = 255
                item.target_scale = 1.0
            
            item.update(dt, y, is_hover, is_selected)
        
        # Button hover animations
        if self.back_button.collidepoint(mouse_pos):
            self.back_hover = min(1.0, self.back_hover + dt * 8)
        else:
            self.back_hover = max(0, self.back_hover - dt * 8)
        
        if self.select_button.collidepoint(mouse_pos) and self.selected_index >= 0:
            self.select_hover = min(1.0, self.select_hover + dt * 8)
            self.select_pulse += dt * 3
        else:
            self.select_hover = max(0, self.select_hover - dt * 8)
            self.select_pulse = 0
    
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
            start_y = 180
            item_height = 50
            spacing = 12
            
            for i, filename in enumerate(self.files):
                y = start_y + i * (item_height + spacing) - self.scroll_offset
                rect = pygame.Rect(80, y, self.screen.get_width() - 160, item_height)
                
                if rect.collidepoint(mouse_pos) and 150 < y < self.screen.get_height() - 150:
                    self.selected_index = i
                    break
        
        elif event.type == pygame.MOUSEWHEEL:
            self.target_scroll -= event.y * 40
            
            # Calculate max scroll
            start_y = 180
            item_height = 50
            spacing = 12
            total_height = len(self.files) * (item_height + spacing)
            max_scroll = max(0, total_height - (self.screen.get_height() - 300))
            
            self.target_scroll = max(0, min(max_scroll, self.target_scroll))
        
        return None
    
    def render(self):
        """Render file chooser with animations"""
        # Animated gradient background
        for y in range(0, self.screen.get_height(), 4):
            progress = y / self.screen.get_height()
            wave = math.sin(self.time * 0.8 + progress * 2) * 5
            color = (
                int(25 + progress * 15 + wave),
                int(28 + progress * 18 + wave),
                int(45 + progress * 20)
            )
            pygame.draw.rect(self.screen, color, (0, y, self.screen.get_width(), 4))
        
        # Title with wave effect
        title_text = "Select Level"
        title_surf = pygame.Surface((700, 100), pygame.SRCALPHA)
        
        for i, char in enumerate(title_text):
            wave_offset = math.sin(self.time * 3 + i * 0.5) * 8
            char_surf = self.font_title.render(char, True, (255, 255, 255))
            
            # Glow effect
            glow_surf = self.font_title.render(char, True, (100, 150, 255))
            glow_alpha = int(150 + math.sin(self.time * 2 + i * 0.3) * 50)
            glow_surf.set_alpha(glow_alpha)
            
            temp_surf = self.font_title.render(title_text[:i], True, (255, 255, 255))
            char_x = temp_surf.get_width()
            
            # Draw glow
            for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
                title_surf.blit(glow_surf, (char_x + dx, int(wave_offset) + dy))
            
            # Draw character
            title_surf.blit(char_surf, (char_x, int(wave_offset)))
        
        title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(title_surf, title_rect)
        
        # Back button with hover animation
        back_scale = 1.0 + self.back_hover * 0.1
        scaled_back = pygame.Rect(
            int(self.back_button.centerx - self.back_button.width * back_scale / 2),
            int(self.back_button.centery - self.back_button.height * back_scale / 2),
            int(self.back_button.width * back_scale),
            int(self.back_button.height * back_scale)
        )
        
        # Glow
        if self.back_hover > 0:
            glow_surf = pygame.Surface((scaled_back.width + 20, scaled_back.height + 20), pygame.SRCALPHA)
            alpha = int(80 * self.back_hover)
            pygame.draw.rect(glow_surf, (100, 100, 150, alpha), glow_surf.get_rect(), border_radius=8)
            self.screen.blit(glow_surf, (scaled_back.x - 10, scaled_back.y - 10))
        
        # Button
        color_intensity = int(self.back_hover * 40)
        button_color = (70 + color_intensity, 70 + color_intensity, 90 + color_intensity)
        pygame.draw.rect(self.screen, button_color, scaled_back, border_radius=8)
        pygame.draw.rect(self.screen, (120, 120, 160), scaled_back, 2, border_radius=8)
        
        # Text
        back_text = self.font_item.render("← Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=scaled_back.center)
        self.screen.blit(back_text, back_rect)
        
        # File list container with border
        list_area = pygame.Rect(60, 150, self.screen.get_width() - 120, self.screen.get_height() - 280)
        
        # Container shadow
        shadow_surf = pygame.Surface((list_area.width + 10, list_area.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect(), border_radius=12)
        self.screen.blit(shadow_surf, (list_area.x - 5, list_area.y - 5))
        
        # Container background
        container_surf = pygame.Surface((list_area.width, list_area.height), pygame.SRCALPHA)
        pygame.draw.rect(container_surf, (30, 33, 45, 200), container_surf.get_rect(), border_radius=10)
        self.screen.blit(container_surf, list_area.topleft)
        
        pygame.draw.rect(self.screen, (80, 90, 120), list_area, 2, border_radius=10)
        
        # Clip region for file items
        clip_rect = list_area.inflate(-20, -20)
        self.screen.set_clip(clip_rect)
        
        # File list or empty message
        if not self.files:
            no_files = self.font_item.render("No board files found", True, (150, 150, 170))
            no_files_rect = no_files.get_rect(center=list_area.center)
            self.screen.blit(no_files, no_files_rect)
            
            hint = self.font_small.render("Place .txt files in the 'boards/' directory", True, (120, 120, 140))
            hint_rect = hint.get_rect(center=(list_area.centerx, list_area.centery + 40))
            self.screen.blit(hint, hint_rect)
        else:
            item_height = 50
            
            for item in self.file_items:
                if item.current_y < 140 or item.current_y > self.screen.get_height() - 140:
                    continue
                
                # Calculate item rect
                item_width = int((self.screen.get_width() - 160) * item.scale)
                item_x = 80 + (self.screen.get_width() - 160 - item_width) // 2
                rect = pygame.Rect(item_x, int(item.current_y), item_width, item_height)
                
                # Selection glow
                if item.select_intensity > 0:
                    glow_surf = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
                    alpha = int(120 * item.select_intensity)
                    pygame.draw.rect(glow_surf, (100, 150, 255, alpha), glow_surf.get_rect(), border_radius=10)
                    self.screen.blit(glow_surf, (rect.x - 10, rect.y - 10))
                
                # Item background
                base_color = 60 if item.select_intensity > 0 else 50
                hover_boost = int(item.hover_intensity * 20)
                select_boost = int(item.select_intensity * 40)
                
                item_color = (
                    base_color + hover_boost + select_boost,
                    base_color + hover_boost + select_boost + 20,
                    base_color + 10 + hover_boost + select_boost + 40
                )
                
                item_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                alpha = int(item.alpha)
                pygame.draw.rect(item_surf, (*item_color, alpha), item_surf.get_rect(), border_radius=8)
                self.screen.blit(item_surf, rect.topleft)
                
                # Border
                border_color = (
                    100 + int(item.select_intensity * 100),
                    120 + int(item.select_intensity * 80),
                    140 + int(item.hover_intensity * 60)
                )
                pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)
                
                # Level number indicator
                level_num = item.filename.replace("level", "").replace(".txt", "").strip()
                if level_num.isdigit():
                    num_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
                    pygame.draw.circle(num_surf, (80, 100, 140, alpha), (20, 20), 18)
                    pygame.draw.circle(num_surf, (120, 140, 180), (20, 20), 18, 2)
                    
                    num_text = self.font_small.render(level_num, True, (255, 255, 255))
                    num_text.set_alpha(alpha)
                    num_rect = num_text.get_rect(center=(20, 20))
                    num_surf.blit(num_text, num_rect)
                    
                    self.screen.blit(num_surf, (rect.left + 10, rect.centery - 20))
                
                # File name
                text = self.font_item.render(item.filename, True, (255, 255, 255))
                text.set_alpha(alpha)
                text_rect = text.get_rect(midleft=(rect.left + 60, rect.centery))
                self.screen.blit(text, text_rect)
                
                # Hover indicator
                if item.hover_intensity > 0:
                    indicator_x = rect.right - 15
                    indicator_alpha = int(200 * item.hover_intensity)
                    pygame.draw.circle(self.screen, (150, 200, 255, indicator_alpha), 
                                     (indicator_x, rect.centery), 6)
        
        # Reset clip
        self.screen.set_clip(None)
        
        # Select button (only if something is selected)
        if self.selected_index >= 0:
            # Pulse animation
            pulse_scale = 1.0 + math.sin(self.select_pulse) * 0.05 * self.select_hover
            hover_scale = 1.0 + self.select_hover * 0.08
            total_scale = pulse_scale * hover_scale
            
            scaled_select = pygame.Rect(
                int(self.select_button.centerx - self.select_button.width * total_scale / 2),
                int(self.select_button.centery - self.select_button.height * total_scale / 2),
                int(self.select_button.width * total_scale),
                int(self.select_button.height * total_scale)
            )
            
            # Glow
            glow_intensity = 0.6 + self.select_hover * 0.4
            glow_surf = pygame.Surface((scaled_select.width + 40, scaled_select.height + 40), pygame.SRCALPHA)
            alpha = int(100 * glow_intensity)
            pygame.draw.rect(glow_surf, (100, 200, 100, alpha), glow_surf.get_rect(), border_radius=15)
            self.screen.blit(glow_surf, (scaled_select.x - 20, scaled_select.y - 20))
            
            # Button
            color_boost = int(self.select_hover * 50)
            button_color = (70 + color_boost, 180 + color_boost, 70 + color_boost)
            pygame.draw.rect(self.screen, button_color, scaled_select, border_radius=12)
            
            # Highlight
            highlight = scaled_select.copy()
            highlight.height = highlight.height // 2
            pygame.draw.rect(self.screen, (120 + color_boost, min(220 + color_boost,255), 120 + color_boost), 
                           highlight, border_radius=12)
            
            # Border
            pygame.draw.rect(self.screen, (150, 255, 150), scaled_select, 3, border_radius=12)
            
            # Text
            select_text = self.font_item.render("Load Level →", True, (255, 255, 255))
            select_rect = select_text.get_rect(center=scaled_select.center)
            
            # Text shadow
            shadow = self.font_item.render("Load Level →", True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(scaled_select.centerx + 2, scaled_select.centery + 2))
            self.screen.blit(shadow, shadow_rect)
            
            self.screen.blit(select_text, select_rect)
        
        # Scroll indicator
        if len(self.files) > 8:
            scroll_track_height = self.screen.get_height() - 320
            scroll_track = pygame.Rect(self.screen.get_width() - 40, 160, 8, scroll_track_height)
            pygame.draw.rect(self.screen, (60, 65, 80), scroll_track, border_radius=4)
            
            # Calculate scroll thumb position
            start_y = 180
            item_height = 50
            spacing = 12
            total_height = len(self.files) * (item_height + spacing)
            max_scroll = max(1, total_height - (self.screen.get_height() - 300))
            
            scroll_ratio = self.scroll_offset / max_scroll
            thumb_height = max(30, int(scroll_track_height * (scroll_track_height / total_height)))
            thumb_y = scroll_track.y + int((scroll_track_height - thumb_height) * scroll_ratio)
            
            thumb_rect = pygame.Rect(scroll_track.x - 2, thumb_y, 12, thumb_height)
            pygame.draw.rect(self.screen, (120, 140, 180), thumb_rect, border_radius=6)