import pygame
import random
from config import *

class DigitalRain:
    def __init__(self, screen):
        self.screen = screen
        self.drops = []
        self.font = pygame.font.SysFont('arial', 14)
        self.setup_drops()

    def setup_drops(self):
        for _ in range(50):
            self.drops.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(-SCREEN_HEIGHT, 0),
                'speed': random.randint(5, 15),
                'chars': [random.choice(MATRIX_CHARS) for _ in range(20)],
                'length': random.randint(10, 30)
            })

    def update_and_draw(self):
        for drop in self.drops:
            # Draw characters with fading effect
            for i, char in enumerate(drop['chars']):
                y_pos = drop['y'] + i * 15
                alpha = max(0, 255 - i * 15)
                text = self.font.render(char, True, MATRIX_GREEN)
                text.set_alpha(alpha)
                self.screen.blit(text, (drop['x'], y_pos))
            
            # Update position
            drop['y'] += drop['speed']
            if drop['y'] > SCREEN_HEIGHT:
                drop['y'] = random.randint(-200, -100)
                drop['x'] = random.randint(0, SCREEN_WIDTH)

class CyberGrid:
    def __init__(self, screen):
        self.screen = screen
        self.offset = 0
        self.grid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
    def draw(self):
        self.grid_surface.fill((0, 0, 0, 0))
        
        # Draw horizontal lines
        for y in range(0, SCREEN_HEIGHT + GRID_SIZE, GRID_SIZE):
            y_pos = (y + self.offset) % SCREEN_HEIGHT
            pygame.draw.line(self.grid_surface, GRID_COLOR, (0, y_pos), 
                           (SCREEN_WIDTH, y_pos), 1)
            
        # Draw vertical lines
        for x in range(0, SCREEN_WIDTH + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(self.grid_surface, GRID_COLOR, (x, 0), 
                           (x, SCREEN_HEIGHT), 1)
        
        self.screen.blit(self.grid_surface, (0, 0))
        self.offset = (self.offset + 1) % GRID_SIZE

class DataParticles:
    def __init__(self, screen):
        self.screen = screen
        self.particles = []
        self.setup_particles()

    def setup_particles(self):
        for _ in range(PARTICLE_COUNT):
            self.particles.append({
                'pos': pygame.Vector2(random.randint(0, SCREEN_WIDTH),
                                    random.randint(0, SCREEN_HEIGHT)),
                'vel': pygame.Vector2(random.uniform(-2, 2),
                                    random.uniform(-2, 2)),
                'size': random.randint(2, 5),
                'color': random.choice([NEON_GREEN, NEON_BLUE, CYBER_PINK])
            })

    def update_and_draw(self):
        for p in self.particles:
            # Update position
            p['pos'] += p['vel']
            
            # Wrap around screen
            p['pos'].x = p['pos'].x % SCREEN_WIDTH
            p['pos'].y = p['pos'].y % SCREEN_HEIGHT
            
            # Draw particle with glow effect
            for i in range(GLOW_INTENSITY):
                size = p['size'] + i * 2
                alpha = 255 // (i + 1)
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*p['color'], alpha), (size, size), size)
                self.screen.blit(surf, p['pos'] - pygame.Vector2(size, size)) 