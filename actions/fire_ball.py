import pygame
import math
import random

class FireBall(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=6, spread_angle=30):
        super().__init__()
        # Charger le sprite sheet de la boule de feu
        self.sprite_sheet = pygame.image.load('./assets/sprites/effects/All_Fire_Bullet_Pixel_16x16.png').convert_alpha()
        self.rect = pygame.Rect(x, y, 16, 16)
        self.pos = [x, y]

        self.speed = speed
        self.frame_index = 0
        self.animation_speed = 0.2
        self.current_direction = direction
        self.damage = 0.5
        self.active = True
        self.countdown = 5000
        self.score = 10

        # Déterminer l’angle avec un petit cône aléatoire
        base_angle = {"up": -90, "down": 90, "left": 180, "right": 0}.get(direction, 0)
        angle_variation = random.uniform(-spread_angle, spread_angle)
        angle = math.radians(base_angle + angle_variation)
        self.velocity = [math.cos(angle) * self.speed, math.sin(angle) * self.speed]

        # Animations par direction (mêmes frames que pour Player mais dans un autre sheet)
        self.animations = {
            'down': self.load_row(2),
            'left': self.load_row(2),
            'right': self.load_row(2),
            'up': self.load_row(2)
        }

        self.image = self.animations[self.current_direction][0]

    def get_image(self, x, y):
        """Récupère une frame depuis le sprite sheet"""
        image = pygame.Surface((16, 16), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 16, 16))
        return image

    def load_row(self, row):
        """Charge une ligne de 4 frames à partir du sprite sheet"""
        return [self.get_image(col * 16, row * 16) for col in range(4)]

    def update(self):
        # Avancer
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.rect.topleft = (int(self.pos[0]), int(self.pos[1]))

        # Animation
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.current_direction]):
            self.frame_index = 0
        self.image = self.animations[self.current_direction][int(self.frame_index)]

        # Kill si trop loin de la zone active
        if (self.pos[0] < -2000 or self.pos[0] > 20000 or
            self.pos[1] < -2000 or self.pos[1] > 20000):
            self.kill()

