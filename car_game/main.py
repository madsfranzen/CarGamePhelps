import pygame
import sys
from config import *
from game_objects.car import Car
from game_objects.road import Road
from game_objects.obstacle import ObstacleManager
from renderer import GameRenderer
from car_game.menu import Menu

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Car Game")
        self.clock = pygame.time.Clock()
        self.menu = Menu(self.screen)
        self.state = "menu"  # menu, playing
        self.reset_game()

    def reset_game(self):
        self.car = Car()
        self.road = Road()
        self.obstacles = ObstacleManager()
        self.renderer = GameRenderer(self.screen)
        
        # Add game references
        self.car.game = self
        self.road.game = self
        
        self.auto_scroll = True
        self.running = True
        self.game_over = False
        self.score = 0
        self.distance = 0
        self.speed_multiplier = 1.0
        self.high_score = 0

    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.auto_scroll = not self.auto_scroll
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_a:  # Toggle AI mode
                    self.car.toggle_ai_mode()

        return self.running

    def update(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.car.update(keys, self.road)
        
        if self.auto_scroll:
            self.road.scroll()
            # Update distance and score
            self.distance += SCROLL_SPEED
            self.score = int(self.distance / 10)
            
            # Update high score if current score is higher
            if self.score > self.high_score:
                self.high_score = self.score
        
        self.obstacles.update(self.road)

        # Check for collisions
        if self.obstacles.check_collision(self.car):
            self.game_over = True

    def render(self):
        self.screen.fill(GREEN)
        self.renderer.render_game(self.road, self.car, self.obstacles)
        
        # Render score and high score
        score_text = self.renderer.debug_font.render(f"Distance: {int(self.distance)}m", True, WHITE)
        high_score_text = self.renderer.debug_font.render(f"High Score: {self.high_score}", True, WHITE)
        points_text = self.renderer.debug_font.render(f"Points: {self.score}", True, WHITE)
        
        self.screen.blit(score_text, (10, 70))
        self.screen.blit(high_score_text, (10, 100))
        self.screen.blit(points_text, (10, 130))

        if self.game_over:
            # Show game over message with final score
            game_over_text = self.renderer.debug_font.render(
                f"Game Over! Final Score: {self.score}", True, RED)
            restart_text = self.renderer.debug_font.render(
                "Press R to restart", True, RED)
            
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
            
            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(restart_text, restart_rect)

    def run(self):
        while True:
            if self.state == "menu":
                action = self.menu.handle_events()
                if action == "quit":
                    break
                elif action == "start_game":
                    self.state = "playing"
                self.menu.render()
            
            elif self.state == "playing":
                if not self.handle_game_events():
                    break
                self.update()
                self.render()
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit() 