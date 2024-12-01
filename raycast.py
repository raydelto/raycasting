import pygame
import math

# CONSTANTS

# Screen dimensions
WIDTH = 1250
HEIGHT = 720
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
TILE = 100  # Size of the map tile

# Calculation constants
ROUNDING_ERROR = 0.00001
ANGLE_STEP = 0.02

# Mini-map scale
MAP_SCALE = 100
MAP_TILE = TILE // MAP_SCALE

# Field of view settings
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 300  # Number of rays for raycasting
MAX_DEPTH = 800  # Max depth of field
DELTA_ANGLE = FOV / NUM_RAYS  # Angle between rays
DIST = NUM_RAYS / (2 * math.tan(HALF_FOV))  # Distance from the player to the projection plane
PROJ_COEFF = 3 * DIST * TILE  # Projection coefficient
SCALE = WIDTH // NUM_RAYS  # Scale of the projected walls

# Color definitions
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 150)
BROWN = (139, 69, 19)

# AUXILIARY FUNCTIONS


# Convert world coordinates to map coordinates
def to_map_coords(x, y):
    return (x // TILE) * TILE, (y // TILE) * TILE


# CLASSES

class Map:
    def __init__(self):
        self.text_map = [
            'XXXXXXXXXXXX',
            'X..........X',
            'X....X..XX..X',
            'X..X.......X',
            'X..X..XX...X',
            'X.X....X...X',
            'X.X..X..XX.X',
            'X....X.....X',
            'XXXXXXXXXXXXX'
        ]

        # Create a set of coordinates for walls in the world map
        self.world_map = set()
        for j, row in enumerate(self.text_map):
            for i, char in enumerate(row):
                if char == 'X':
                    self.world_map.add((i * TILE, j * TILE))


class Player:
    def __init__(self):
        self.x = HALF_WIDTH + ROUNDING_ERROR
        self.y = HALF_HEIGHT + ROUNDING_ERROR
        self.angle = 0
        self.speed = 1

    @property
    def pos(self):
        return (self.x, self.y)

    def move(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.x += self.speed * cos_a
            self.y += self.speed * sin_a
        if keys[pygame.K_s]:
            self.x += -self.speed * cos_a
            self.y += -self.speed * sin_a
        if keys[pygame.K_a]:
            self.x += self.speed * sin_a
            self.y += -self.speed * cos_a
        if keys[pygame.K_d]:
            self.x += -self.speed * sin_a
            self.y += self.speed * cos_a
        if keys[pygame.K_LEFT]:
            self.angle -= ANGLE_STEP
        if keys[pygame.K_RIGHT]:
            self.angle += ANGLE_STEP


class Renderer:
    def __init__(self, screen, player, map):
        self.screen = screen
        self.player = player
        self.map = map

    def draw_background(self):
        # Draw Ceiling
        pygame.draw.rect(self.screen, BLUE, (0, 0, WIDTH, HALF_HEIGHT))

        # Draw Floor
        pygame.draw.rect(self.screen, GRAY, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))

    # Draw walls using raycasting
    def draw_walls(self):
        mapped_x, mapped_y = to_map_coords(self.player.x, self.player.y)
        cur_angle = self.player.angle - HALF_FOV
        for ray in range(NUM_RAYS):
            sin_a = math.sin(cur_angle)
            cos_a = math.cos(cur_angle)
            sin_a = sin_a if sin_a else ROUNDING_ERROR  # Avoid division by zero
            cos_a = cos_a if cos_a else ROUNDING_ERROR  # Avoid division by zero

            # Vertical lines
            x, dx = (mapped_x + TILE, 1) if cos_a >= 0 else (mapped_x, -1)
            for i in range(0, WIDTH, TILE):
                depth_v = (x - self.player.x) / cos_a
                y = self.player.y + depth_v * sin_a
                if to_map_coords(x + dx, y) in self.map.world_map:
                    break
                x += dx * TILE

            # Horizontal lines
            y, dy = (mapped_y + TILE, 1) if sin_a >= 0 else (mapped_y, -1)
            for i in range(0, HEIGHT, TILE):
                depth_h = (y - self.player.y) / sin_a
                x = self.player.x + depth_h * cos_a
                if to_map_coords(x, y + dy) in self.map.world_map:
                    break
                y += dy * TILE

            # Determine the closest wall
            depth = depth_v if depth_v < depth_h else depth_h
            depth *= math.cos(self.player.angle - cur_angle)  # Remove fish-eye effect
            proj_height = PROJ_COEFF / depth  # Calculate projected wall height
            pygame.draw.rect(self.screen, BROWN, (ray * SCALE, HALF_HEIGHT - proj_height // 2, SCALE, proj_height))
            cur_angle += DELTA_ANGLE


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    player = Player()
    map = Map()
    renderer = Renderer(screen, player, map)

    while True:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        player.move()
        screen.fill(BLACK)

        renderer.draw_background()
        renderer.draw_walls()

        pygame.display.flip()


if __name__ == "__main__":
    main()
