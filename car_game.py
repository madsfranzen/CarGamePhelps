import pygame
import sys

# Initialize Pygame
pygame.init()

# Game parameters
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Road parameters
ROAD_WIDTH = 300  # Total width of the road
LANE_WIDTH = ROAD_WIDTH / 3  # Width of each lane
ROAD_LEFT_EDGE = (SCREEN_WIDTH - ROAD_WIDTH) / 2  # X coordinate of left edge
ROAD_RIGHT_EDGE = ROAD_LEFT_EDGE + ROAD_WIDTH  # X coordinate of right edge

# Car parameters
CAR_WIDTH = 40
CAR_HEIGHT = 70
CAR_SPEED = 5
car_x = SCREEN_WIDTH // 2 - CAR_WIDTH // 2
car_y = SCREEN_HEIGHT - CAR_HEIGHT - 20
car_lane = 1  # 0: left, 1: middle, 2: right

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)

def draw_road():
    # Road background
    pygame.draw.rect(screen, GRAY, [ROAD_LEFT_EDGE, 0, ROAD_WIDTH, SCREEN_HEIGHT])
    
    # Lane markings
    lane1_x = ROAD_LEFT_EDGE + LANE_WIDTH
    lane2_x = ROAD_LEFT_EDGE + LANE_WIDTH * 2
    
    for y in range(0, SCREEN_HEIGHT, 40):
        # Dashed lines between lanes
        pygame.draw.rect(screen, WHITE, [lane1_x - 2, y, 4, 20])
        pygame.draw.rect(screen, WHITE, [lane2_x - 2, y, 4, 20])
    
    # Solid lines on road edges
    pygame.draw.rect(screen, WHITE, [ROAD_LEFT_EDGE, 0, 4, SCREEN_HEIGHT])
    pygame.draw.rect(screen, WHITE, [ROAD_RIGHT_EDGE - 4, 0, 4, SCREEN_HEIGHT])

def draw_car(is_off_road):
    car_color = RED if is_off_road else GREEN
    pygame.draw.rect(screen, car_color, [car_x, car_y, CAR_WIDTH, CAR_HEIGHT])

def main_game_loop():
    global car_x, car_y, car_lane
    
    running = True
    while running:
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Horizontal movement (left/right)
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and car_x > 0:
            car_x -= CAR_SPEED
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and car_x < SCREEN_WIDTH - CAR_WIDTH:
            car_x += CAR_SPEED
        
        # Vertical movement (up/down) - optional
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and car_y > 0:
            car_y -= CAR_SPEED
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and car_y < SCREEN_HEIGHT - CAR_HEIGHT:
            car_y += CAR_SPEED
        
        # Update car's lane position
        car_center_x = car_x + CAR_WIDTH // 2
        if car_center_x < ROAD_LEFT_EDGE + LANE_WIDTH:
            car_lane = 0
        elif car_center_x < ROAD_LEFT_EDGE + 2 * LANE_WIDTH:
            car_lane = 1
        else:
            car_lane = 2
        
        # Check if car is off the road
        is_off_road = car_x < ROAD_LEFT_EDGE or car_x + CAR_WIDTH > ROAD_RIGHT_EDGE
        
        # Clear the screen
        screen.fill(BLACK)
        
        # Draw game elements
        draw_road()
        draw_car(is_off_road)
        
        # Display parameters for debugging
        font = pygame.font.Font(None, 30)
        text = font.render(f"Car position: ({car_x}, {car_y}) | Lane: {car_lane} | Off road: {is_off_road}", 
                          True, WHITE)
        screen.blit(text, (10, 10))
        
        # Road boundaries info
        boundaries_text = font.render(f"Road: Left edge = {ROAD_LEFT_EDGE}, Right edge = {ROAD_RIGHT_EDGE}", 
                                     True, WHITE)
        screen.blit(boundaries_text, (10, 40))
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_game_loop()
