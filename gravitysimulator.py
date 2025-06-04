import pygame
import math
import random

WIDTH, HEIGHT = 1100, 800
WINDOW_TITLE = "Gravity Simulator"
FPS = 60
SCALED_G = 2000
TIME_STEP = 0.1
MIN_DISTANCE = 10
MAX_VELOCITY = 100
VELOCITY_SCALE_FACTOR = 0.1

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 100)
BLUE = (100, 150, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
GREY = (150, 150, 150)
COLORS = [RED, BLUE, YELLOW, GREEN, (150, 150, 255), (255, 150, 150)]

class Body:
    def __init__(self, x, y, radius, mass, color, initial_velocity_x=0, initial_velocity_y=0):
        self.pos = pygame.math.Vector2(x, y)
        self.radius = max(3, int(radius))
        self.mass = mass if mass != 0 else 1
        self.color = color
        self.velocity = pygame.math.Vector2(initial_velocity_x, initial_velocity_y)
        self.force = pygame.math.Vector2(0, 0)
        self.trail = []

    def add_force(self, force_vector):
        self.force += force_vector

    def update_position(self):
        if self.mass == 0:
            return

        acceleration = self.force / self.mass
        self.velocity += acceleration * TIME_STEP

        if self.velocity.length_squared() > MAX_VELOCITY**2:
            self.velocity.scale_to_length(MAX_VELOCITY)

        self.pos += self.velocity * TIME_STEP
        self.force = pygame.math.Vector2(0, 0)

        self.trail.append(tuple(self.pos))
        if len(self.trail) > 150:
            self.trail.pop(0)

    def draw(self, screen):
        if len(self.trail) > 1:
            try:
                pygame.draw.lines(screen, self.color, False, self.trail, 1)
            except TypeError:
                pass
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), int(self.radius))

    def get_radius_for_mass(mass_val):
        return max(3, int(math.sqrt(abs(mass_val) / math.pi) * 2.5))

    def __repr__(self):
        return f"Body(pos={self.pos}, mass={self.mass}, vel={self.velocity}, radius={self.radius})"

def calculate_gravitational_force(body1, body2):
    direction_vector = body2.pos - body1.pos
    distance_sq = direction_vector.length_squared()

    if distance_sq < MIN_DISTANCE**2:
        if distance_sq < (body1.radius + body2.radius)**2 / 4:
            return pygame.math.Vector2(0, 0)
        distance_sq = MIN_DISTANCE**2

    force_magnitude = SCALED_G * (body1.mass * body2.mass) / distance_sq
    return direction_vector.normalize() * force_magnitude

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    bodies = [
        Body(WIDTH / 2, HEIGHT / 2, Body.get_radius_for_mass(10000), 10000, YELLOW),
        Body(WIDTH / 2 + 200, HEIGHT / 2, Body.get_radius_for_mass(70), 70, BLUE, initial_velocity_y=-25),
        Body(WIDTH / 2 - 100, HEIGHT / 2 - 150, Body.get_radius_for_mass(30), 30, GREEN, initial_velocity_x=15, initial_velocity_y=15)
    ]

    running = True
    paused = False
    show_help = True

    current_new_body_mass = 50
    min_mass, max_mass = 5, 5000
    mass_increment = 5

    creating_body_phase = None
    slingshot_start_pos = None
    slingshot_end_pos = None

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    bodies = [
                        Body(WIDTH / 2, HEIGHT / 2, Body.get_radius_for_mass(10000), 10000, YELLOW),
                        Body(WIDTH / 2 + 200, HEIGHT / 2, Body.get_radius_for_mass(70), 70, BLUE, initial_velocity_y=-25),
                        Body(WIDTH / 2 - 100, HEIGHT / 2 - 150, Body.get_radius_for_mass(30), 30, GREEN, initial_velocity_x=15, initial_velocity_y=15)
                    ]
                    creating_body_phase = None
                elif event.key == pygame.K_h:
                    show_help = not show_help
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                    current_new_body_mass = min(max_mass, current_new_body_mass + mass_increment)
                elif event.key == pygame.K_MINUS:
                    current_new_body_mass = max(min_mass, current_new_body_mass - mass_increment)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if creating_body_phase is None:
                        creating_body_phase = "setting_velocity"
                        slingshot_start_pos = event.pos
                        slingshot_end_pos = event.pos
                elif event.button == 3:
                    if len(bodies) > 1 and bodies[0].mass == 10000:
                        bodies = [bodies[0]]
                    else:
                        bodies = []
                    creating_body_phase = None

            if event.type == pygame.MOUSEMOTION:
                if creating_body_phase == "setting_velocity" and slingshot_start_pos:
                    slingshot_end_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and creating_body_phase == "setting_velocity":
                    if slingshot_start_pos and slingshot_end_pos:
                        start_x, start_y = slingshot_start_pos
                        end_x, end_y = slingshot_end_pos

                        vel_x = (start_x - end_x) * VELOCITY_SCALE_FACTOR
                        vel_y = (start_y - end_y) * VELOCITY_SCALE_FACTOR

                        new_radius = Body.get_radius_for_mass(current_new_body_mass)
                        new_color = random.choice(COLORS)
                        new_body = Body(start_x, start_y, new_radius, current_new_body_mass, new_color, vel_x, vel_y)
                        bodies.append(new_body)
                    creating_body_phase = None
                    slingshot_start_pos = None
                    slingshot_end_pos = None

        if not paused:
            for i in range(len(bodies)):
                for j in range(i + 1, len(bodies)):
                    body1 = bodies[i]
                    body2 = bodies[j]
                    force = calculate_gravitational_force(body1, body2)
                    body1.add_force(force)
                    body2.add_force(-force)

            temp_bodies = list(bodies)
            for body in temp_bodies:
                body.update_position()

                is_sun = bodies and body == bodies[0] and body.mass >= 10000
                if not is_sun and not (-WIDTH * 0.5 < body.pos.x < WIDTH * 1.5 and -HEIGHT * 0.5 < body.pos.y < HEIGHT * 1.5):
                    try:
                        bodies.remove(body)
                    except ValueError:
                        pass

        screen.fill(BLACK)
        for body in bodies:
            body.draw(screen)

        if creating_body_phase == "setting_velocity" and slingshot_start_pos:
            preview_radius = Body.get_radius_for_mass(current_new_body_mass)
            pygame.draw.circle(screen, GREY, slingshot_start_pos, int(preview_radius), 1)
            if slingshot_end_pos:
                pygame.draw.line(screen, GREY, slingshot_start_pos, slingshot_end_pos, 1)
                pygame.draw.circle(screen, WHITE, slingshot_end_pos, 3)

        if show_help:
            help_text = [
                "Gravity Simulator",
                "-------------------------------------",
                f"Next Body Mass: {current_new_body_mass:.0f} (use +/- to change)",
                "Left Click: Set body position",
                "Hold & Drag Left Mouse: Aim slingshot (drag AWAY from launch direction)",
                "Release Left Mouse: Launch body",
                "Right Click: Clear spawned bodies",
                "SPACE: Pause/Resume",
                "R: Reset simulation",
                "H: Toggle this help",
                "ESC: Quit",
                f"Bodies: {len(bodies)}"
            ]
            for i, line in enumerate(help_text):
                text_surface = font.render(line, True, WHITE)
                screen.blit(text_surface, (10, 10 + i * 20))
        else:
            info_line = f"Mass: {current_new_body_mass:.0f} | Bodies: {len(bodies)} (Press H for help)"
            text_surface = font.render(info_line, True, WHITE)
            screen.blit(text_surface, (10, 10))

        if paused:
            pause_text = font.render("PAUSED", True, YELLOW)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
