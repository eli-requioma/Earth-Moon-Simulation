import pygame
import math
pygame.init()

# Initialize Pygame window
WIDTH, HEIGHT = 3000, 1600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")

ZOOM_SPEED = 0.1 # How much the zoom changes per key press
MIN_ZOOM = 0.5
MAX_ZOOM = 4.0

GAME_SURFACE = pygame.Surface((WIDTH, HEIGHT))

# Zoom variable
zoom_factor = 0.5

# Colors
WHITE = (255,255,255)
ORANGE = (242,131,32)
GREY = (141,138,136)
LIGHT_BROWN = (244,219,196)
BLUE = (70, 139, 172)
RED = (232,57,54)
BROWN = (166,112,92)
YELLOW = (243,206,136)
LIGHT_BLUE = (208,236,240)
DARK_BLUE = (70,104,166)

# Planet class with important functions
class Planet:
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    SCALE = 1000 / AU  # 1AU = 100 pixels
    TIMESTEP = 3600*24 # 1 day

    def compute_orbit_path(self):
        updated_points = []
        for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x, y))
        return updated_points
    
    def __init__(self, a, e, x, y, radius, color, mass): # For initializing planet properties
        #in AU
        self.a = a
        self.e = e
        self.x = x
        self.y = y

        self.radius = radius
        self.color = color
        self.mass = mass

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0

    def set_elliptical_orbit(self, central_body):
        """
        Sets the planet's position at perihelion and velocity for an elliptical orbit.
        """
        G = Planet.G
        AU = Planet.AU
        M = central_body.mass

        # Perihelion distance
        r_p = self.a * AU * (1 - self.e)
        self.x = r_p
        self.y = 0

        # Velocity at perihelion (all tangential, along -y axis)
        v_p = math.sqrt(G * M * (1 + self.e) / (self.a * AU * (1 - self.e)))
        self.x_vel = 0
        self.y_vel = -v_p

    # Draw the planet and its orbit
    def draw(self, surface):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        if len(self.orbit) > 2:
            self.orbit_path = self.compute_orbit_path()
            pygame.draw.lines(surface, self.color, False, self.orbit_path, 2)
        
        pygame.draw.circle(surface, self.color, (x, y), self.radius)

    # Calculate gravitational attraction between two planets
    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    # Update planet position based on gravitational forces
    def update_position(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))

# Handle user input for zooming (Q - zoom in, E - zoom out)
def input():
    global zoom_factor
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        
        # --- ZOOM INPUT ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                zoom_factor += ZOOM_SPEED
            elif event.key == pygame.K_q:
                # Zoom Out (Decrease zoom factor)
                zoom_factor -= ZOOM_SPEED
    
    # Clamp the zoom factor to prevent it from going too far
    zoom_factor = max(MIN_ZOOM, min(MAX_ZOOM, zoom_factor))

# Main simulation
def main():
    run = True
    clock = pygame.time.Clock()

    # pretend this is the earth
    sun = Planet(0, 0, 0, 0, 24, BLUE, 1.98892 * 10**30)
    sun.sun = True

    # Initialize planets with real orbital parameters
    moon = Planet(0.257, 0.0549, 0.257 * Planet.AU, 0, 12, GREY, 3.3010 * 10**23)
    moon.y_vel = -47.87 * 1000

    planets = [sun, moon]
    
    for planet in [moon]:
        planet.set_elliptical_orbit(sun)

    while run:
        clock.tick(60)

        input()

        GAME_SURFACE.fill((0,0,0))
        for planet in planets:
            planet.update_position(planets)
            planet.draw(GAME_SURFACE)

        new_width = int(WIDTH * zoom_factor)
        new_height = int(HEIGHT * zoom_factor)
        scaled_surface = pygame.transform.smoothscale(GAME_SURFACE, (new_width, new_height))
        WIN.fill((50, 50, 50))
        x_offset = (WIDTH - new_width) // 2
        y_offset = (HEIGHT - new_height) // 2
        WIN.blit(scaled_surface, (x_offset, y_offset))
        
        pygame.display.update()

    pygame.quit()

main()