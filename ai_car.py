import pygame # type: ignore
import math

class AICar:
    def __init__(self, x, y, image_path, checkpoints, speed=2.0):
        self.x = x
        self.y = y
        self.angle = 315
        self.speed = speed
        self.checkpoints = checkpoints
        self.current_cp = 0
        self.lap = 0

        self.image = pygame.image.load(image_path).convert_alpha()
        self.original_image = self.image
        self.original_image = pygame.transform.scale(self.original_image, (50, 70))
        self.width, self.height = self.original_image.get_size()

    def update(self):
        target_x, target_y = self.checkpoints[self.current_cp]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        # --- Calculate desired angle (player coordinate system) ---
        target_angle = math.degrees(math.atan2(dx, -dy))
        angle_diff = (target_angle - self.angle + 180) % 360 - 180

        # --- Smooth turning (key to natural movement) ---
        max_turn = 3.0
        self.angle += max(min(angle_diff, max_turn), -max_turn)

        # --- Move forward at constant speed ---
        rad = math.radians(self.angle)
        self.x += math.sin(rad) * self.speed
        self.y -= math.cos(rad) * self.speed

        # --- STRICT checkpoint order (no skipping) ---
        if dist < 65:
            self.current_cp += 1
            if self.current_cp >= len(self.checkpoints):
                self.current_cp = 0
                self.lap += 1

    def draw(self, window, camera_x, camera_y):
        rotated = pygame.transform.rotate(self.original_image, -self.angle)
        rect = rotated.get_rect(center=(self.x - camera_x, self.y - camera_y))
        window.blit(rotated, rect)

