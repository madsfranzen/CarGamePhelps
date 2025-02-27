import pygame
from config import *
from game_objects.obstacle import TrafficCar, Trash, Roadblock
from effects import DigitalRain, CyberGrid, DataParticles
import random

class GameRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.digital_rain = DigitalRain(screen)
        self.cyber_grid = CyberGrid(screen)
        self.particles = DataParticles(screen)
        self.scanline_surface = self._create_scanlines()
        self.debug_font = pygame.font.SysFont('arial', 30)
        self.glow_shader = self._create_glow_shader()

    def _create_scanlines(self):
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, SCAN_LINE_SPACING):
            pygame.draw.line(surface, (0, 0, 0, SCAN_LINE_ALPHA), 
                           (0, y), (SCREEN_WIDTH, y))
        return surface

    def _create_glow_shader(self):
        shader = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        shader.fill((0, 20, 0, 10))
        return shader

    def render_game(self, road, car, obstacles):
        # Draw background effects
        self.screen.fill(DARK_MATRIX)
        self.digital_rain.update_and_draw()
        self.cyber_grid.draw()
        self.particles.update_and_draw()
        
        # Draw road with cyber effect
        self._render_cyber_road(road)
        
        # Draw obstacles with data visualization
        self._render_cyber_obstacles(obstacles)
        
        # Draw car with energy field
        self._render_cyber_car(car, road)
        
        # Draw AI status indicator
        self._render_ai_status(car)
        
        # Apply post-processing effects
        self._apply_post_processing()

    def _render_cyber_road(self, road):
        # Create smooth road using more points for smoother curves
        segment_height = SCREEN_HEIGHT // (ROAD_DETAIL * 2)
        
        # Create points for the road edges
        left_points = []
        right_points = []
        lane1_points = []
        lane2_points = []
        
        # Generate points along the road
        for i in range(ROAD_DETAIL * 2 + 1):
            y = i * segment_height
            left_edge, right_edge = road.get_road_edges(y)
            lane1 = left_edge + LANE_WIDTH
            lane2 = left_edge + LANE_WIDTH * 2
            
            if i > 0:
                prev_left = left_points[-1][0]
                prev_right = right_points[-1][0]
                left_edge = prev_left + (left_edge - prev_left) * 0.7
                right_edge = prev_right + (right_edge - prev_right) * 0.7
            
            left_points.append((left_edge, y))
            right_points.append((right_edge, y))
            lane1_points.append((lane1, y))
            lane2_points.append((lane2, y))
        
        # Draw cyber road
        road_polygon = left_points + right_points[::-1]
        pygame.draw.polygon(self.screen, DARK_MATRIX, road_polygon)
        
        # Draw data stream effects along edges
        for i in range(len(left_points) - 1):
            # Left edge data stream
            pygame.draw.line(self.screen, NEON_BLUE, left_points[i], left_points[i + 1], 3)
            # Right edge data stream
            pygame.draw.line(self.screen, NEON_BLUE, right_points[i], right_points[i + 1], 3)
        
        # Draw lane markings with cyber effect
        self._draw_cyber_lane_markings(lane1_points, road.offset)
        self._draw_cyber_lane_markings(lane2_points, road.offset)

    def _draw_cyber_lane_markings(self, points, road_offset):
        dash_length = 40
        gap_length = 30
        full_cycle = dash_length + gap_length
        start_offset = -(road_offset / 6) % full_cycle
        
        for i in range(len(points) - 1):
            line_pos = i * SCREEN_HEIGHT / (ROAD_DETAIL * 2)
            pos_in_cycle = (line_pos + start_offset) % full_cycle
            if pos_in_cycle < dash_length:
                # Draw neon line
                pygame.draw.line(self.screen, NEON_GREEN, points[i], points[i + 1], 2)
                # Add glow effect
                pygame.draw.line(self.screen, (*NEON_GREEN, 50), points[i], points[i + 1], 4)

    def _render_cyber_scenery(self, scenery):
        # Draw cyber trees and rocks
        for obj in scenery.scenery_objects:
            if obj['type'] == 'tree':
                self._draw_cyber_tree(obj)
            elif obj['type'] == 'rock':
                self._draw_cyber_rock(obj)
            elif obj['type'] == 'bush':
                self._draw_cyber_bush(obj)

    def _draw_cyber_tree(self, tree):
        x, y = tree['x'], tree['y']
        # Draw digital tree trunk
        pygame.draw.rect(self.screen, GRID_COLOR, 
                        [x - 10, y - 40, 20, 40])
        
        # Draw digital foliage
        points = [
            (x, y - 80),
            (x - 30, y - 40),
            (x + 30, y - 40)
        ]
        pygame.draw.polygon(self.screen, NEON_GREEN, points)
        # Add glow effect
        for i in range(2):
            glow_points = [
                (x, y - 82 + i),
                (x - 32 + i, y - 40),
                (x + 32 - i, y - 40)
            ]
            pygame.draw.polygon(self.screen, (*NEON_GREEN, 50), glow_points)

    def _draw_cyber_rock(self, rock):
        x, y = rock['x'], rock['y']
        points = [
            (x, y - 20),
            (x - 20, y),
            (x, y + 20),
            (x + 20, y)
        ]
        # Draw digital rock with wireframe effect
        pygame.draw.polygon(self.screen, GRID_COLOR, points)
        pygame.draw.lines(self.screen, NEON_BLUE, True, points, 2)

    def _draw_cyber_bush(self, bush):
        x, y = bush['x'], bush['y']
        radius = 15
        # Draw digital bush
        pygame.draw.circle(self.screen, NEON_GREEN, (int(x), int(y)), radius)
        # Add circuit pattern
        pygame.draw.circle(self.screen, GRID_COLOR, (int(x), int(y)), radius, 2)
        pygame.draw.line(self.screen, GRID_COLOR, (x - radius, y), (x + radius, y), 2)
        pygame.draw.line(self.screen, GRID_COLOR, (x, y - radius), (x, y + radius), 2)

    def _render_cyber_car(self, car, road):
        # Create energy field around car
        glow_surface = pygame.Surface((CAR_WIDTH + 20, CAR_HEIGHT + 20), pygame.SRCALPHA)
        for i in range(GLOW_INTENSITY):
            alpha = 100 - i * 20
            color = NEON_BLUE if not car.is_off_road(road) else CYBER_PINK
            pygame.draw.rect(glow_surface, (*color, alpha),
                            (i, i, CAR_WIDTH + 20 - i*2, CAR_HEIGHT + 20 - i*2),
                            border_radius=10)
        
        # Draw car base
        car_surface = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, NEON_GREEN, 
                        (0, 0, CAR_WIDTH, CAR_HEIGHT), border_radius=5)
        
        # Add circuit pattern
        pygame.draw.line(car_surface, GRID_COLOR, 
                        (CAR_WIDTH/2, 0), (CAR_WIDTH/2, CAR_HEIGHT), 2)
        pygame.draw.line(car_surface, GRID_COLOR,
                        (0, CAR_HEIGHT/2), (CAR_WIDTH, CAR_HEIGHT/2), 2)
        
        # Add windshield
        window_width = CAR_WIDTH * 0.7
        window_x = (CAR_WIDTH - window_width) / 2
        pygame.draw.rect(car_surface, NEON_BLUE,
                        (window_x, CAR_HEIGHT * 0.2, window_width, CAR_HEIGHT * 0.3),
                        border_radius=3)
        
        # Rotate car
        rotated_glow = pygame.transform.rotate(glow_surface, car.angle)
        rotated_car = pygame.transform.rotate(car_surface, car.angle)
        
        # Position and draw
        glow_rect = rotated_glow.get_rect(center=(car.x + CAR_WIDTH//2, car.y + CAR_HEIGHT//2))
        car_rect = rotated_car.get_rect(center=(car.x + CAR_WIDTH//2, car.y + CAR_HEIGHT//2))
        
        self.screen.blit(rotated_glow, glow_rect.topleft)
        self.screen.blit(rotated_car, car_rect.topleft)

    def _render_cyber_obstacles(self, obstacles):
        for obstacle in obstacles.obstacles:
            if isinstance(obstacle, TrafficCar):
                self._render_cyber_traffic(obstacle)
            elif isinstance(obstacle, Roadblock):
                self._render_data_barrier(obstacle)
            elif isinstance(obstacle, Trash):
                self._render_corrupt_data(obstacle)

    def _apply_post_processing(self):
        # Apply scanlines
        self.screen.blit(self.scanline_surface, (0, 0))
        
        # Apply subtle color shift
        self.screen.blit(self.glow_shader, (0, 0))
        
        # Add chromatic aberration effect
        ...

    def _render_scenery(self, scenery):
        scenery.draw(self.screen)

    def _render_road(self, road):
        # Create smooth road using more points for smoother curves
        segment_height = SCREEN_HEIGHT // (ROAD_DETAIL * 2)  # Doubled detail for smoothness
        
        # Create points for the road edges
        left_points = []
        right_points = []
        lane1_points = []
        lane2_points = []
        
        # Generate points along the road with bezier curve smoothing
        for i in range(ROAD_DETAIL * 2 + 1):
            y = i * segment_height
            left_edge, right_edge = road.get_road_edges(y)
            center = (left_edge + right_edge) / 2
            lane1 = left_edge + LANE_WIDTH
            lane2 = left_edge + LANE_WIDTH * 2
            
            # Add points with slight horizontal interpolation for smoothness
            if i > 0:
                prev_left = left_points[-1][0]
                prev_right = right_points[-1][0]
                left_edge = prev_left + (left_edge - prev_left) * 0.7
                right_edge = prev_right + (right_edge - prev_right) * 0.7
            
            left_points.append((left_edge, y))
            right_points.append((right_edge, y))
            lane1_points.append((lane1, y))
            lane2_points.append((lane2, y))
        
        # Draw road background with anti-aliasing
        road_polygon = left_points + right_points[::-1]
        pygame.draw.polygon(self.screen, GRAY, road_polygon)
        
        # Draw lane markings
        self._draw_lane_markings(lane1_points, road.offset)
        self._draw_lane_markings(lane2_points, road.offset)
        
        # Draw road edges with anti-aliasing
        pygame.draw.aalines(self.screen, WHITE, False, left_points, 4)
        pygame.draw.aalines(self.screen, WHITE, False, right_points, 4)

    def _draw_lane_markings(self, points, road_offset, is_dashed=True):
        if not is_dashed:
            pygame.draw.aalines(self.screen, WHITE, False, points, 4)
            return
        
        # Longer dashes, shorter gaps for a more realistic look
        dash_length = 40  # Increased from 20
        gap_length = 30   # Increased from 20
        full_cycle = dash_length + gap_length
        
        # Thicker lines
        line_width = 6    # Increased from 4
        
        # Slower stripe movement
        stripe_speed_factor = 6  # Increased from 4
        start_offset = -(road_offset / stripe_speed_factor) % full_cycle
        
        # Draw slightly faded stripes
        stripe_color = (255, 255, 255, 200)  # Slightly transparent white
        
        for i in range(len(points) - 1):
            line_pos = i * SCREEN_HEIGHT / (ROAD_DETAIL * 2)
            pos_in_cycle = (line_pos + start_offset) % full_cycle
            if pos_in_cycle < dash_length:
                # Draw thicker anti-aliased line
                pygame.draw.aaline(self.screen, stripe_color, 
                                 points[i], points[i + 1], line_width)
                
                # Add a slight glow effect
                glow_color = (255, 255, 255, 50)  # Very transparent white
                pygame.draw.aaline(self.screen, glow_color,
                                 points[i], points[i + 1], line_width + 2)

    def _render_obstacles(self, obstacles):
        for obstacle in obstacles.obstacles:
            if isinstance(obstacle, TrafficCar):
                # Draw a simplified car
                pygame.draw.rect(self.screen, obstacle.color, 
                               [obstacle.x, obstacle.y, obstacle.width, obstacle.height])
                # Add car details (windows, etc.)
                window_color = (200, 200, 255)
                window_width = obstacle.width * 0.6
                window_x = obstacle.x + (obstacle.width - window_width) / 2
                pygame.draw.rect(self.screen, window_color,
                               [window_x, obstacle.y + obstacle.height * 0.2,
                                window_width, obstacle.height * 0.3])
            
            elif isinstance(obstacle, Trash):
                # Draw rotated trash
                surface = pygame.Surface((obstacle.width, obstacle.height), pygame.SRCALPHA)
                pygame.draw.polygon(surface, obstacle.color, [
                    (0, obstacle.height/2),
                    (obstacle.width/2, 0),
                    (obstacle.width, obstacle.height/2),
                    (obstacle.width/2, obstacle.height)
                ])
                rotated = pygame.transform.rotate(surface, obstacle.rotation)
                self.screen.blit(rotated, (obstacle.x, obstacle.y))
            
            elif isinstance(obstacle, Roadblock):
                # Draw striped roadblock
                pygame.draw.rect(self.screen, obstacle.color,
                               [obstacle.x, obstacle.y, obstacle.width, obstacle.height])
                stripe_color = (255, 255, 0)  # Yellow stripes
                for i in range(0, int(obstacle.width), 20):
                    pygame.draw.line(self.screen, stripe_color,
                                   (obstacle.x + i, obstacle.y),
                                   (obstacle.x + i + 10, obstacle.y + obstacle.height),
                                   5)

    def _render_car(self, car, road):
        # Create a car surface with the correct color
        temp_car_surface = car.surface.copy()
        if car.is_off_road(road):
            red_overlay = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
            red_overlay.fill((255, 0, 0, 100))  # Semi-transparent red
            temp_car_surface.blit(red_overlay, (0, 0))
        
        # Rotate the car surface
        rotated_car = pygame.transform.rotate(temp_car_surface, car.angle)
        rotated_rect = rotated_car.get_rect(center=(car.x + CAR_WIDTH//2, car.y + CAR_HEIGHT//2))
        
        # Draw the rotated car
        self.screen.blit(rotated_car, rotated_rect.topleft)

    def _render_debug_info(self, car, road):
        # Car position and lane info
        text = self.debug_font.render(
            f"Car position: ({car.x:.1f}, {car.y:.1f}) | Lane: {car.lane} | Off road: {car.is_off_road(road)}",
            True, WHITE)
        self.screen.blit(text, (10, 10))
        
        # Road boundaries and car angle
        left_edge, right_edge = road.get_road_edges(car.y + CAR_HEIGHT / 2)
        boundaries_text = self.debug_font.render(
            f"Road: Left = {left_edge:.1f}, Right = {right_edge:.1f} | Angle: {car.angle:.1f}°",
            True, WHITE)
        self.screen.blit(boundaries_text, (10, 40))

    def _render_cyber_traffic(self, obstacle):
        # Draw base with glow
        for i in range(GLOW_INTENSITY):
            alpha = 100 - i * 20
            pygame.draw.rect(self.screen, (*NEON_BLUE, alpha),
                            [obstacle.x - i, obstacle.y - i, 
                             obstacle.width + i*2, obstacle.height + i*2],
                            border_radius=5)
        
        # Draw main body
        pygame.draw.rect(self.screen, MATRIX_GREEN,
                        [obstacle.x, obstacle.y, obstacle.width, obstacle.height],
                        border_radius=5)
        
        # Add circuit pattern
        pygame.draw.line(self.screen, GRID_COLOR,
                        (obstacle.x + obstacle.width/2, obstacle.y),
                        (obstacle.x + obstacle.width/2, obstacle.y + obstacle.height), 2)
        
        # Add data stream window
        window_width = obstacle.width * 0.6
        window_x = obstacle.x + (obstacle.width - window_width) / 2
        pygame.draw.rect(self.screen, NEON_BLUE,
                        [window_x, obstacle.y + obstacle.height * 0.2,
                         window_width, obstacle.height * 0.3],
                        border_radius=3)

    def _render_data_barrier(self, obstacle):
        # Draw base
        pygame.draw.rect(self.screen, CYBER_PINK,
                        [obstacle.x, obstacle.y, obstacle.width, obstacle.height])
        
        # Add warning stripes
        for i in range(0, int(obstacle.width), 20):
            pygame.draw.line(self.screen, NEON_BLUE,
                            (obstacle.x + i, obstacle.y),
                            (obstacle.x + i + 10, obstacle.y + obstacle.height),
                            5)
        
        # Add glowing outline
        pygame.draw.rect(self.screen, (*CYBER_PINK, 100),
                        [obstacle.x - 2, obstacle.y - 2,
                         obstacle.width + 4, obstacle.height + 4], 2)

    def _render_corrupt_data(self, obstacle):
        # Create glitch effect surface
        surface = pygame.Surface((obstacle.width, obstacle.height), pygame.SRCALPHA)
        
        # Draw glitch polygons
        glitch_points = [
            (0, obstacle.height/2),
            (obstacle.width/2, 0),
            (obstacle.width, obstacle.height/2),
            (obstacle.width/2, obstacle.height)
        ]
        
        # Draw multiple layers with different colors for glitch effect
        pygame.draw.polygon(surface, (*CYBER_PINK, 150), glitch_points)
        pygame.draw.polygon(surface, (*NEON_BLUE, 100), 
                           [(p[0]+2, p[1]-2) for p in glitch_points])
        pygame.draw.polygon(surface, (*NEON_GREEN, 50), 
                           [(p[0]-2, p[1]+2) for p in glitch_points])
        
        # Rotate and draw
        rotated = pygame.transform.rotate(surface, obstacle.rotation)
        self.screen.blit(rotated, (obstacle.x, obstacle.y))

    def _render_ai_status(self, car):
        # Position in top-right corner
        x = SCREEN_WIDTH - 150
        y = 20
        width = 120
        height = 40
        
        # Create background with glow effect
        for i in range(GLOW_INTENSITY):
            alpha = 100 - i * 20
            color = NEON_GREEN if car.ai_mode else CYBER_PINK
            pygame.draw.rect(self.screen, (*color, alpha),
                            [x - i, y - i, width + i*2, height + i*2],
                            border_radius=5)

        # Draw main box
        pygame.draw.rect(self.screen, DARK_MATRIX,
                        [x, y, width, height],
                        border_radius=5)
        
        # Draw text
        text = "AI: ON" if car.ai_mode else "AI: OFF"
        text_color = NEON_GREEN if car.ai_mode else CYBER_PINK
        text_surface = self.debug_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
        
        # Add circuit pattern
        pygame.draw.line(self.screen, GRID_COLOR,
                        (x + 10, y + height//2),
                        (x + width - 10, y + height//2), 1)
        pygame.draw.line(self.screen, GRID_COLOR,
                        (x + width//2, y + 5),
                        (x + width//2, y + height - 5), 1)
        
        # Draw text with glitch effect if AI is on
        if car.ai_mode:
            glitch_offset = random.randint(-1, 1)
            glitch_surface = self.debug_font.render(text, True, NEON_BLUE)
            self.screen.blit(glitch_surface, 
                            (text_rect.x + glitch_offset, text_rect.y))
        
        self.screen.blit(text_surface, text_rect) 