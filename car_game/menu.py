import pygame
import random
from config import *
from effects import DigitalRain, CyberGrid, DataParticles

class Button:
    def __init__(self, text, pos, size=(200, 50), color=NEON_BLUE):
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.text = text
        self.color = color
        self.hover_color = (*color[:3], 255)  # Full alpha when hovered
        self.is_hovered = False
        self.glitch_offset = 0
        self.glitch_timer = 0
        
    def draw(self, screen, font):
        # Create glitch effect
        self.glitch_timer = (self.glitch_timer + 1) % 30
        if self.glitch_timer == 0:
            self.glitch_offset = random.randint(-2, 2)
        
        # Draw button with cyber effect
        color = self.hover_color if self.is_hovered else self.color
        
        # Draw multiple layers for glow effect
        for i in range(GLOW_INTENSITY):
            alpha = 100 - i * 20
            pygame.draw.rect(screen, (*color[:3], alpha),
                           pygame.Rect(self.rect.x - i, self.rect.y - i,
                                     self.rect.width + i*2, self.rect.height + i*2),
                           border_radius=2)
        
        # Draw main button
        pygame.draw.rect(screen, color, self.rect, border_radius=2)
        
        # Draw text with glitch effect
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Draw glitch copies
        if self.is_hovered:
            glitch_colors = [CYBER_PINK, NEON_BLUE, NEON_GREEN]
            for i, color in enumerate(glitch_colors):
                glitch_surface = font.render(self.text, True, color)
                offset = self.glitch_offset * (i + 1)
                screen.blit(glitch_surface, 
                          (text_rect.x + offset, text_rect.y))
        
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.digital_rain = DigitalRain(screen)
        self.cyber_grid = CyberGrid(screen)
        self.particles = DataParticles(screen)
        self.font = pygame.font.SysFont('arial', 40)
        self.title_font = pygame.font.SysFont('arial', 80)
        self.state = "main"
        self.settings = {
            "difficulty": 1,
            "music_volume": 0.7,
            "sfx_volume": 1.0,
            "traffic_density": 1.0,
            "night_mode": False
        }
        self.leaderboard = self._load_leaderboard()
        self._init_buttons()
        self.title_glitch = 0
        self.frame_count = 0

    def _init_buttons(self):
        center_x = SCREEN_WIDTH // 2 - 100
        # Main menu buttons
        self.main_buttons = [
            Button("Start Game", (center_x, 200), color=GREEN),
            Button("Settings", (center_x, 270), color=BLUE),
            Button("Leaderboard", (center_x, 340), color=PURPLE),
            Button("Quit", (center_x, 410), color=RED)
        ]
        
        # Settings buttons
        self.settings_buttons = [
            Button("Difficulty", (center_x, 200)),
            Button("Music Volume", (center_x, 270)),
            Button("SFX Volume", (center_x, 340)),
            Button("Traffic Density", (center_x, 410)),
            Button("Night Mode", (center_x, 480)),
            Button("Back", (center_x, 550), color=RED)
        ]
        
        # Leaderboard buttons
        self.leaderboard_buttons = [
            Button("Back", (center_x, 500), color=RED)
        ]

    def _load_leaderboard(self):
        # TODO: Load from file
        return [
            ("Player1", 1000),
            ("Player2", 800),
            ("Player3", 600),
            ("Player4", 400),
            ("Player5", 200)
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if self.state == "main":
                for i, button in enumerate(self.main_buttons):
                    if button.handle_event(event):
                        if i == 0: return "start_game"
                        elif i == 1: self.state = "settings"
                        elif i == 2: self.state = "leaderboard"
                        elif i == 3: return "quit"
            
            elif self.state == "settings":
                for i, button in enumerate(self.settings_buttons):
                    if button.handle_event(event):
                        if i == 0:  # Difficulty
                            self.settings["difficulty"] = (self.settings["difficulty"] + 1) % 3
                        elif i == 1:  # Music Volume
                            self.settings["music_volume"] = (self.settings["music_volume"] + 0.1) % 1.1
                        elif i == 2:  # SFX Volume
                            self.settings["sfx_volume"] = (self.settings["sfx_volume"] + 0.1) % 1.1
                        elif i == 3:  # Traffic Density
                            self.settings["traffic_density"] = (self.settings["traffic_density"] + 0.25) % 1.25
                        elif i == 4:  # Night Mode
                            self.settings["night_mode"] = not self.settings["night_mode"]
                        elif i == 5:  # Back
                            self.state = "main"
            
            elif self.state == "leaderboard":
                for button in self.leaderboard_buttons:
                    if button.handle_event(event):
                        self.state = "main"
        
        return None

    def render(self):
        # Draw background effects
        self.screen.fill(DARK_MATRIX)
        self.digital_rain.update_and_draw()
        self.cyber_grid.draw()
        self.particles.update_and_draw()

        if self.state == "main":
            self._render_main_menu()
        elif self.state == "settings":
            self._render_settings()
        elif self.state == "leaderboard":
            self._render_leaderboard()

    def _render_main_menu(self):
        # Animate title with glitch effect
        self.frame_count = (self.frame_count + 1) % 60
        if self.frame_count == 0:
            self.title_glitch = random.randint(-3, 3)

        # Draw glitched title
        title_colors = [CYBER_PINK, NEON_BLUE, NEON_GREEN]
        for i, color in enumerate(title_colors):
            title = self.title_font.render("CYBER DRIVE", True, color)
            offset = self.title_glitch * (i + 1)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2 + offset, 100))
            self.screen.blit(title, title_rect)

        # Draw main title
        title = self.title_font.render("CYBER DRIVE", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw buttons
        for button in self.main_buttons:
            button.draw(self.screen, self.font)

    def _render_settings(self):
        # Draw title
        title = self.title_font.render("Settings", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw buttons and current values
        difficulty_names = ["Easy", "Normal", "Hard"]
        values = [
            f"Difficulty: {difficulty_names[self.settings['difficulty']]}",
            f"Music: {int(self.settings['music_volume'] * 100)}%",
            f"SFX: {int(self.settings['sfx_volume'] * 100)}%",
            f"Traffic: {int(self.settings['traffic_density'] * 100)}%",
            f"Night Mode: {'On' if self.settings['night_mode'] else 'Off'}",
            "Back"
        ]
        
        for button, value in zip(self.settings_buttons, values):
            button.text = value
            button.draw(self.screen, self.font)

    def _render_leaderboard(self):
        # Draw title
        title = self.title_font.render("Leaderboard", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title, title_rect)
        
        # Draw scores
        for i, (name, score) in enumerate(self.leaderboard):
            text = self.font.render(f"{i+1}. {name}: {score}", True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH//2 - 100, 200 + i * 50))
        
        # Draw back button
        for button in self.leaderboard_buttons:
            button.draw(self.screen, self.font) 