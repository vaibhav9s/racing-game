import pygame # type: ignore
import math

class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 315

        # Movement physics
        self.vx = 0.0
        self.vy = 0.0
        self.acceleration = 0.25
        self.friction = 0.02
        self.max_speed = 7.0
        self.turn_speed = 4.0

        # Car appearance
        self.original_image = pygame.image.load("img/f1.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (50, 70))
        self.width, self.height = self.original_image.get_size()

    def update(self, keys, track, camera_x, camera_y):
        # Forward direction based on angle
        rad = math.radians(self.angle)
        forward_x = math.sin(rad)
        forward_y = -math.cos(rad)

        # Accelerate forward/backward
        if keys[pygame.K_UP]:
            self.vx += forward_x * self.acceleration
            self.vy += forward_y * self.acceleration
        elif keys[pygame.K_DOWN]:
            self.vx -= forward_x * self.acceleration * 0.6
            self.vy -= forward_y * self.acceleration * 0.6

        # Apply friction
        self.vx *= (1 - self.friction)
        self.vy *= (1 - self.friction)

        # Limit speed
        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vx *= scale
            self.vy *= scale

        # Turning
        if speed > 0.2:
            turn_rate = self.turn_speed * (speed / self.max_speed)
            if keys[pygame.K_LEFT]:
                self.angle -= turn_rate
            if keys[pygame.K_RIGHT]:
                self.angle += turn_rate

        # Update position
        self.x += self.vx
        self.y += self.vy

        # --- Simple Collision: White Area Check ---
        pixel_x = int(self.x)
        pixel_y = int(self.y)

        if 0 <= pixel_x < track.get_width() and 0 <= pixel_y < track.get_height():
            r, g, b, _ = track.get_at((pixel_x, pixel_y))

            # Road is gray asphalt ≈ (118,118,118)
            if not (110 <= r <= 130 and 110 <= g <= 130 and 110 <= b <= 130):
                self.vx *= 0.90
                self.vy *= 0.90


    def draw(self, window):
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        car_surface.fill(self.color)

        rotated = pygame.transform.rotate(car_surface, -self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        window.blit(rotated, rect.topleft)

    def draw_at(self, window, x, y):
        rotated = pygame.transform.rotate(self.original_image, -self.angle)
        rect = rotated.get_rect(center=(x, y))
        window.blit(rotated, rect)

