import random
import pygame
from config import *
from .ai_driver import AIDriver

class BaseObstacle:
    def __init__(self, lane, y):
        self.lane = lane
        self.y = y
        self.width = 40
        self.height = 40
        self.x = 0  # Will be updated based on lane
        self.speed = 0  # For moving obstacles like traffic

    def update(self, road):
        lane_positions = road.get_lane_positions(self.y)
        self.x = lane_positions[self.lane] - self.width / 2
        self.y += SCROLL_SPEED + self.speed

    def collides_with_car(self, car):
        return (car.x < self.x + self.width and
                car.x + CAR_WIDTH > self.x and
                car.y < self.y + self.height and
                car.y + CAR_HEIGHT > self.y)

class TrafficCar(BaseObstacle):
    def __init__(self, lane, y):
        super().__init__(lane, y)
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.color = MATRIX_GREEN
        self.speed = -SCROLL_SPEED * 0.5
        self.target_lane = lane
        self.is_changing_lanes = False
        self.decision_cooldown = 0
        self.decision_interval = 15
        self.lane_change_cooldown = 0

    def update(self, road):
        if self.lane_change_cooldown > 0:
            self.lane_change_cooldown -= 1

        # AI decision making
        self.decision_cooldown -= 1
        if self.decision_cooldown <= 0 and not self.is_changing_lanes:
            self.decision_cooldown = self.decision_interval
            # Get all obstacles including other cars
            all_obstacles = []
            for obs in self.game.obstacles.obstacles:
                if hasattr(obs, 'lane'):
                    all_obstacles.append(obs)
            # Add player car
            if hasattr(self.game, 'car'):
                all_obstacles.append(self.game.car)
            
            # Remove self from obstacles
            all_obstacles = [obs for obs in all_obstacles if obs != self]
            
            decision = AIDriver.make_decision(self, all_obstacles, look_ahead=200)
            if decision is not None:
                new_lane = self.lane + decision
                if 0 <= new_lane <= 2:  # Verify lane is valid
                    self.target_lane = new_lane
                    self.is_changing_lanes = True
                    self.lane_change_cooldown = LANE_CHANGE_COOLDOWN_MAX

        # Update position
        lane_positions = road.get_lane_positions(self.y)
        
        if self.is_changing_lanes:
            target_x = lane_positions[self.target_lane]
            car_center_x = self.x + self.width / 2
            
            direction = 1 if target_x > car_center_x else -1
            distance = min(LANE_CHANGE_SPEED * 0.5, abs(target_x - car_center_x))
            
            self.x += direction * distance
            
            if abs(car_center_x - target_x) < LANE_CHANGE_SPEED * 0.5:
                self.x = target_x - self.width / 2
                self.lane = self.target_lane
                self.is_changing_lanes = False
        else:
            target_x = lane_positions[self.lane]
            self.x = target_x - self.width / 2

        # Move forward
        self.y += SCROLL_SPEED + self.speed

class Trash(BaseObstacle):
    def __init__(self, lane, y):
        super().__init__(lane, y)
        self.width = 30
        self.height = 30
        self.color = (139, 69, 19)  # Brown for trash
        self.rotation = random.randint(0, 360)

class Roadblock(BaseObstacle):
    def __init__(self, lane, y):
        super().__init__(lane, y)
        self.width = LANE_WIDTH * 0.8
        self.height = 40
        self.color = (255, 140, 0)  # Orange for roadblocks

class ObstacleManager:
    def __init__(self):
        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_delay = 60
        self.obstacle_types = [
            (TrafficCar, 60),    # (type, weight)
            (Trash, 30),
            (Roadblock, 10)
        ]
        self.total_weight = sum(weight for _, weight in self.obstacle_types)

    def _choose_obstacle_type(self):
        r = random.randint(0, self.total_weight - 1)
        for obstacle_type, weight in self.obstacle_types:
            r -= weight
            if r < 0:
                return obstacle_type
        return TrafficCar

    def update(self, road):
        # Update and remove off-screen obstacles
        for obstacle in self.obstacles[:]:
            if isinstance(obstacle, TrafficCar) and not hasattr(obstacle, 'game'):
                obstacle.game = road.game  # Ensure traffic cars have game reference
            obstacle.update(road)
            if obstacle.y > SCREEN_HEIGHT + 100:
                self.obstacles.remove(obstacle)

        # Spawn new obstacles
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0
            
            lane = random.randint(0, 2)
            obstacle_type = self._choose_obstacle_type()
            
            # Check spacing for traffic cars
            if obstacle_type == TrafficCar:
                for obs in self.obstacles:
                    if isinstance(obs, TrafficCar) and abs(obs.y - (-50)) < CAR_HEIGHT * 2:
                        return

            # Spawn at the top of the screen
            new_obstacle = obstacle_type(lane, -50)
            if isinstance(new_obstacle, TrafficCar):
                new_obstacle.game = road.game  # Give traffic cars access to game state
            self.obstacles.append(new_obstacle)

    def get_all_cars(self):
        # Return traffic cars (excluding player car to avoid circular reference)
        return [obs for obs in self.obstacles if isinstance(obs, TrafficCar)]

    def check_collision(self, car):
        for obstacle in self.obstacles:
            if obstacle.collides_with_car(car):
                return True
        return False

    def reset(self):
        self.obstacles.clear()
        self.spawn_timer = 0 