import pygame
from config import *
from .ai_driver import AIDriver

class Car:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2 - CAR_WIDTH // 2
        self.y = SCREEN_HEIGHT - CAR_HEIGHT - 20
        self.lane = 1
        self.angle = 0
        self.target_angle = 0
        self.target_lane = 1
        self.is_changing_lanes = False
        self.lane_change_cooldown = 0
        self.moving_direction = 0
        self.surface = self._create_car_surface()
        self.ai_mode = True  # Start in AI mode
        self.decision_cooldown = 0
        self.decision_interval = 10  # Frames between AI decisions

    def _create_car_surface(self):
        """Create a detailed car surface"""
        surface = pygame.Surface((CAR_WIDTH, CAR_HEIGHT), pygame.SRCALPHA)
        
        # Car body
        pygame.draw.rect(surface, CAR_BODY_COLOR, [0, 0, CAR_WIDTH, CAR_HEIGHT], border_radius=8)
        
        # Roof area
        roof_width = int(CAR_WIDTH * 0.8)
        roof_start = (CAR_WIDTH - roof_width) // 2
        pygame.draw.rect(surface, CAR_BODY_COLOR, 
                        [roof_start, CAR_HEIGHT//4, roof_width, CAR_HEIGHT//2], 
                        border_radius=5)
        
        # Windows
        # Windshield
        pygame.draw.polygon(surface, CAR_WINDOW_COLOR, [
            (roof_start + 3, CAR_HEIGHT//4 + 5),
            (roof_start + roof_width - 3, CAR_HEIGHT//4 + 5),
            (roof_start + roof_width - 8, CAR_HEIGHT//4 + 15),
            (roof_start + 8, CAR_HEIGHT//4 + 15)
        ])
        
        # Rear window
        pygame.draw.polygon(surface, CAR_WINDOW_COLOR, [
            (roof_start + 3, CAR_HEIGHT*3//4 - 5),
            (roof_start + roof_width - 3, CAR_HEIGHT*3//4 - 5),
            (roof_start + roof_width - 8, CAR_HEIGHT*3//4 - 15),
            (roof_start + 8, CAR_HEIGHT*3//4 - 15)
        ])
        
        # Side windows
        window_height = CAR_HEIGHT//4
        side_window_y = CAR_HEIGHT//3
        pygame.draw.rect(surface, CAR_WINDOW_COLOR,
                        [roof_start, side_window_y, 5, window_height])
        pygame.draw.rect(surface, CAR_WINDOW_COLOR,
                        [roof_start + roof_width - 5, side_window_y, 5, window_height])
        
        # Headlights
        headlight_size = 6
        pygame.draw.rect(surface, CAR_LIGHT_COLOR,
                        [3, 3, headlight_size, headlight_size], border_radius=2)
        pygame.draw.rect(surface, CAR_LIGHT_COLOR,
                        [CAR_WIDTH - headlight_size - 3, 3, headlight_size, headlight_size], border_radius=2)
        
        # Taillights
        pygame.draw.rect(surface, (255, 0, 0),
                        [3, CAR_HEIGHT - headlight_size - 3, headlight_size, headlight_size], border_radius=2)
        pygame.draw.rect(surface, (255, 0, 0),
                        [CAR_WIDTH - headlight_size - 3, CAR_HEIGHT - headlight_size - 3, headlight_size, headlight_size], border_radius=2)
        
        # Wheels
        wheel_width = 8
        wheel_height = 14
        pygame.draw.rect(surface, CAR_DETAIL_COLOR, [
            -2, CAR_HEIGHT//5, wheel_width, wheel_height], border_radius=3)
        pygame.draw.rect(surface, CAR_DETAIL_COLOR, [
            CAR_WIDTH - wheel_width + 2, CAR_HEIGHT//5, wheel_width, wheel_height], border_radius=3)
        pygame.draw.rect(surface, CAR_DETAIL_COLOR, [
            -2, CAR_HEIGHT*3//4, wheel_width, wheel_height], border_radius=3)
        pygame.draw.rect(surface, CAR_DETAIL_COLOR, [
            CAR_WIDTH - wheel_width + 2, CAR_HEIGHT*3//4, wheel_width, wheel_height], border_radius=3)
        
        return surface

    def _handle_input(self, keys):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not self.is_changing_lanes and self.lane_change_cooldown == 0:
            if self.lane > 0:
                self.target_lane = self.lane - 1
                self.is_changing_lanes = True
                self.lane_change_cooldown = LANE_CHANGE_COOLDOWN_MAX
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not self.is_changing_lanes and self.lane_change_cooldown == 0:
            if self.lane < 2:
                self.target_lane = self.lane + 1
                self.is_changing_lanes = True
                self.lane_change_cooldown = LANE_CHANGE_COOLDOWN_MAX

    def _update_position(self, road):
        lane_positions = road.get_lane_positions(self.y + CAR_HEIGHT / 2)
        
        if self.is_changing_lanes:
            target_x = lane_positions[self.target_lane]
            car_center_x = self.x + CAR_WIDTH / 2
            
            direction = 1 if target_x > car_center_x else -1
            distance = min(LANE_CHANGE_SPEED, abs(target_x - car_center_x))
            
            self.x += direction * distance
            
            if abs(car_center_x - target_x) < LANE_CHANGE_SPEED:
                self.x = target_x - CAR_WIDTH / 2
                self.lane = self.target_lane
                self.is_changing_lanes = False
        else:
            target_x = lane_positions[self.lane]
            self.x = target_x - CAR_WIDTH / 2

    def _update_rotation(self):
        if self.angle < self.target_angle:
            self.angle = min(self.angle + ROTATION_SPEED, self.target_angle)
        elif self.angle > self.target_angle:
            self.angle = max(self.angle - ROTATION_SPEED, self.target_angle)

    def is_off_road(self, road):
        corners = [
            (self.x, self.y),  # Top left
            (self.x + CAR_WIDTH, self.y),  # Top right
            (self.x, self.y + CAR_HEIGHT),  # Bottom left
            (self.x + CAR_WIDTH, self.y + CAR_HEIGHT)  # Bottom right
        ]
        
        for corner_x, corner_y in corners:
            left_edge, right_edge = road.get_road_edges(corner_y)
            if corner_x < left_edge or corner_x > right_edge:
                return True
        return False

    def update(self, keys, road):
        if self.ai_mode:
            self._ai_update(road)
        else:
            self._player_update(keys, road)

    def _player_update(self, keys, road):
        if self.lane_change_cooldown > 0:
            self.lane_change_cooldown -= 1

        # Only handle input if not already changing lanes
        if not self.is_changing_lanes and self.lane_change_cooldown == 0:
            if keys[pygame.K_LEFT] and self.lane > 0:
                self.target_lane = self.lane - 1
                self.is_changing_lanes = True
                self.lane_change_cooldown = LANE_CHANGE_COOLDOWN_MAX
            elif keys[pygame.K_RIGHT] and self.lane < 2:
                self.target_lane = self.lane + 1
                self.is_changing_lanes = True
                self.lane_change_cooldown = LANE_CHANGE_COOLDOWN_MAX

        # Update position and rotation
        self._update_position(road)
        self._update_rotation()

        # Update lane change if in progress
        if self.is_changing_lanes:
            self._update_lane_change(road)

        # Update car angle based on road
        target_x = road.get_lane_positions(self.y + CAR_HEIGHT/2)[self.lane]
        self.angle = -((target_x - self.x) / ROAD_WIDTH) * MAX_ROTATION

    def _ai_update(self, road):
        if self.lane_change_cooldown > 0:
            self.lane_change_cooldown -= 1

        # AI decision making - more frequent checks for player car
        self.decision_cooldown -= 1
        if self.decision_cooldown <= 0:  # Removed the is_changing_lanes check to allow emergency maneuvers
            self.decision_cooldown = 5  # More frequent decisions for player car
            # Get all obstacles
            all_obstacles = []
            
            # Add regular obstacles
            for obs in self.game.obstacles.obstacles:
                if hasattr(obs, 'lane'):  # Make sure obstacle has required attributes
                    all_obstacles.append(obs)
            
            # Add traffic cars
            for car in self.game.obstacles.get_all_cars():
                if car != self and car not in all_obstacles:
                    all_obstacles.append(car)
            
            decision = AIDriver.make_decision(self, all_obstacles, look_ahead=400)  # Longer look ahead for player
            if decision is not None:
                new_lane = self.lane + decision
                if 0 <= new_lane <= 2:  # Verify lane is valid
                    self.target_lane = new_lane
                    self.is_changing_lanes = True
                    self.lane_change_cooldown = LANE_CHANGE_COOLDOWN_MAX // 2  # Faster cooldown for player

        # Update position and rotation
        self._update_position(road)
        self._update_rotation()

        # Update lane change if in progress
        if self.is_changing_lanes:
            self._update_lane_change(road)

        # Update car angle based on road
        target_x = road.get_lane_positions(self.y + CAR_HEIGHT/2)[self.lane]
        self.angle = -((target_x - self.x) / ROAD_WIDTH) * MAX_ROTATION

    def _update_lane_change(self, road):
        lane_positions = road.get_lane_positions(self.y + CAR_HEIGHT / 2)
        target_x = lane_positions[self.target_lane]
        
        # Smoother lane changes
        car_center_x = self.x + CAR_WIDTH / 2
        direction = 1 if target_x > car_center_x else -1
        distance = min(LANE_CHANGE_SPEED * 1.5, abs(target_x - car_center_x))  # Faster lane changes
        
        self.x += direction * distance
        
        if abs(car_center_x - target_x) < LANE_CHANGE_SPEED:
            self.x = target_x - CAR_WIDTH / 2
            self.lane = self.target_lane
            self.is_changing_lanes = False

    def toggle_ai_mode(self):
        self.ai_mode = not self.ai_mode 