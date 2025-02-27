import pygame
import sys
from config import *
from game_objects.car import Car
from game_objects.road import Road
from game_objects.scenery import SceneryManager
from game_objects.obstacle import ObstacleManager
from renderer import GameRenderer

class Game:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.reset_game()

    def reset_game(self):
        self.car = Car()
        self.road = Road()
        self.scenery = SceneryManager()
        self.obstacles = ObstacleManager()
        self.renderer = GameRenderer(screen)
        self.auto_scroll = True
        self.running = True
        self.game_over = False
        self.score = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.auto_scroll = not self.auto_scroll
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def update(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.car.update(keys, self.road)
        
        if self.auto_scroll:
            self.road.scroll()
            self.score += 1
        
        self.scenery.update(self.road)
        self.obstacles.update(self.road)

        # Check for collisions
        if self.obstacles.check_collision(self.car):
            self.game_over = True

    def render(self):
        self.screen.fill(GREEN)
        self.renderer.render_game(self.scenery, self.road, self.car, self.obstacles)
        
        # Render score
        score_text = self.renderer.debug_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 70))

        if self.game_over:
            game_over_text = self.renderer.debug_font.render("Game Over! Press R to restart", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(game_over_text, text_rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit() 