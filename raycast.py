import pygame
import math

# Screen dimensions
WIDTH = 1250
HEIGHT = 720
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 100  # Frames per second
TILE = 100  # Size of the map tile

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

# Player settings
player_pos = (HALF_WIDTH + 0.00001, HALF_HEIGHT + 0.00001)
player_angle = 0
player_speed = 1

# Color definitions
BLACK = (0, 0, 0)

# Text map representation of the world
text_map = [
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
world_map = set()
for j, row in enumerate(text_map):
    for i, char in enumerate(row):
        if char == 'X':
            world_map.add((i * TILE, j * TILE))

# Player class to handle player attributes and movement
class Player:
    def __init__(self):
        self.x, self.y = player_pos
        self.angle = player_angle

    @property
    def pos(self):
        return (self.x, self.y)

    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.x += player_speed * cos_a
            self.y += player_speed * sin_a
        if keys[pygame.K_s]:
            self.x += -player_speed * cos_a
            self.y += -player_speed * sin_a
        if keys[pygame.K_a]:
            self.x += player_speed * sin_a
            self.y += -player_speed * cos_a
        if keys[pygame.K_d]:
            self.x += -player_speed * sin_a
            self.y += player_speed * cos_a
        if keys[pygame.K_LEFT]:
            self.angle -= 0.02
        if keys[pygame.K_RIGHT]:
            self.angle += 0.02

# Drawing class to handle the rendering of the game world
class Drawing:
    def __init__(self, sc):
        self.sc = sc

    # Draw the background (ceiling and floor)
    def background(self):
        pygame.draw.rect(self.sc, BLACK, (0, 0, WIDTH, HALF_HEIGHT))
        pygame.draw.rect(self.sc, BLACK, (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT))

    # Draw the 3D world based on the player's position and angle
    def world(self, player_pos, player_angle):
        ray_casting(self.sc, player_pos, player_angle)

# Convert world coordinates to map coordinates
def mapping(a, b):
    return (a // TILE) * TILE, (b // TILE) * TILE

# Calculate dynamic wall colors
def get_wall_color():
    ticks = pygame.time.get_ticks()
    r = (127 * (1 + math.sin(ticks * 0.0005)) + 128) % 256
    g = (127 * (1 + math.sin(ticks * 0.001 + 2)) + 128) % 256
    b = (127 * (1 + math.sin(ticks * 0.0015 + 4)) + 128) % 256
    return (int(r), int(g), int(b))

# Perform raycasting to render the walls
def ray_casting(sc, player_pos, player_angle):
    ox, oy = player_pos
    xm, ym = mapping(ox, oy)
    cur_angle = player_angle - HALF_FOV
    for ray in range(NUM_RAYS):
        sin_a = math.sin(cur_angle)
        cos_a = math.cos(cur_angle)
        sin_a = sin_a if sin_a else 0.000001  # Avoid division by zero
        cos_a = cos_a if cos_a else 0.000001  # Avoid division by zero

        # Vertical lines
        x, dx = (xm + TILE, 1) if cos_a >= 0 else (xm, -1)
        for i in range(0, WIDTH, TILE):
            depth_v = (x - ox) / cos_a
            y = oy + depth_v * sin_a
            if mapping(x + dx, y) in world_map:
                break
            x += dx * TILE

        # Horizontal lines
        y, dy = (ym + TILE, 1) if sin_a >= 0 else (ym, -1)
        for i in range(0, HEIGHT, TILE):
            depth_h = (y - oy) / sin_a
            x = ox + depth_h * cos_a
            if mapping(x, y + dy) in world_map:
                break
            y += dy * TILE

        # Determine the closest wall
        depth = depth_v if depth_v < depth_h else depth_h
        depth *= math.cos(player_angle - cur_angle)  # Remove fish-eye effect
        proj_height = PROJ_COEFF / depth  # Calculate projected wall height
        color = get_wall_color()  # Get dynamic wall color
        while color == (0, 0, 0):
            color = get_wall_color()
        pygame.draw.rect(sc, color, (ray * SCALE, HALF_HEIGHT - proj_height // 2, SCALE, proj_height))
        cur_angle += DELTA_ANGLE

# Initialize Pygame
pygame.init()
sc = pygame.display.set_mode((WIDTH, HEIGHT))
player = Player()
drawing = Drawing(sc)

clock = pygame.time.Clock()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    player.movement()
    sc.fill(BLACK)

    drawing.background()
    drawing.world(player.pos, player.angle)

    pygame.display.flip()
    clock.tick(FPS)
