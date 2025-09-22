import pygame
import math
import random

from utils.animation import (
    load_sprite_sheet,
    load_directional_animations,
    advance_animation,
)


class FireBall(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=6, spread_angle=30):
        super().__init__()
        # Charger le sprite sheet de la boule de feu
        self.sprite_sheet = load_sprite_sheet('./assets/sprites/effects/All_Fire_Bullet_Pixel_16x16.png')
        self.rect = pygame.Rect(x, y, 16, 16)
        self.pos = [x, y]

        self.speed = speed
        self.frame_index = 0
        self.animation_speed = 0.2
        self.current_direction = direction
        self.damage = 0.01
        self.active = True
        self.countdown = 5000
        self.score = 10

        # Determiner l'angle avec un petit cone aleatoire
        base_angle = {"up": -90, "down": 90, "left": 180, "right": 0}.get(direction, 0)
        angle_variation = random.uniform(-spread_angle, spread_angle)
        angle = math.radians(base_angle + angle_variation)
        self.velocity = [math.cos(angle) * self.speed, math.sin(angle) * self.speed]

        # Animations par direction (identiques pour chaque orientation)
        self.animations = load_directional_animations(
            self.sprite_sheet,
            16,
            16,
            {
                'down': 2,
                'left': 2,
                'right': 2,
                'up': 2,
            },
        )
        self.image = self.animations[self.current_direction][0]

    def update(self):
        # Avancer
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.rect.topleft = (int(self.pos[0]), int(self.pos[1]))

        # Animation
        frames = self.animations[self.current_direction]
        self.frame_index, self.image = advance_animation(
            self.frame_index,
            frames,
            self.animation_speed,
            True,
        )

        # Kill si trop loin de la zone active
        if (self.pos[0] < -2000 or self.pos[0] > 20000 or
            self.pos[1] < -2000 or self.pos[1] > 20000):
            self.kill()
