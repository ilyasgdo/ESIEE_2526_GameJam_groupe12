import pygame
import math
import random

class AllyBot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Utiliser le même sprite sheet que le joueur mais avec une couleur différente
        self.sprite_sheet = pygame.image.load('assets/sprites/player/BIRDSPRITESHEET_Blue.png').convert_alpha()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.position = [float(x), float(y)]
        self.speed = 1.5  # Vitesse modérée
        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_direction = 'up'  # Direction principale vers le haut
        
        # Variables pour mouvement aléatoire vers le haut
        self.target_x = x
        self.target_y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.2
        self.friction = 0.9
        
        # Variables pour le mouvement aléatoire
        self.direction_change_timer = 0
        self.direction_change_interval = random.randint(60, 180)  # 1-3 secondes
        self.random_direction_x = 0
        self.random_direction_y = -1  # Tendance vers le haut
        
        # Limites de mouvement (pour rester dans les limites de la carte)
        self.map_width = 1280  # 40 * 32
        self.map_height = 6400  # 200 * 32
        
        # Récupérer toutes les frames (même système que le joueur)
        self.animations = {
            'down': self.load_row(0),
            'left': self.load_row(2),
            'right': self.load_row(1),
            'up': self.load_row(3)
        }
        
        # Appliquer une teinte verte pour distinguer le bot allié
        self.apply_tint((200, 255, 200))  # Teinte verte
        
        self.image = self.animations['up'][0]
        self.is_moving = True

    def get_image(self, x, y):
        """Récupère une image du sprite sheet"""
        image = pygame.Surface((32, 32), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image

    def load_row(self, row):
        """Charge une ligne d'animation"""
        return [self.get_image(col * 32, row * 32) for col in range(4)]

    def apply_tint(self, color):
        """Applique une teinte colorée aux sprites"""
        for direction in self.animations:
            for i, frame in enumerate(self.animations[direction]):
                # Créer une surface avec la teinte
                tinted_frame = frame.copy()
                tint_surface = pygame.Surface(frame.get_size(), pygame.SRCALPHA)
                tint_surface.fill((*color, 128))  # Alpha de 128 pour un effet subtil
                tinted_frame.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                self.animations[direction][i] = tinted_frame

    def change_animation(self, direction):
        """Change la direction d'animation"""
        if direction != self.current_direction:
            self.current_direction = direction
            self.frame_index = 0

    def update_random_movement(self):
        """Met à jour le mouvement aléatoire avec tendance vers le haut"""
        self.direction_change_timer += 1
        
        # Changer de direction aléatoirement
        if self.direction_change_timer >= self.direction_change_interval:
            self.direction_change_timer = 0
            self.direction_change_interval = random.randint(60, 180)
            
            # Mouvement aléatoire avec forte tendance vers le haut
            self.random_direction_x = random.uniform(-0.5, 0.5)  # Mouvement horizontal léger
            self.random_direction_y = random.uniform(-1.0, -0.3)  # Mouvement vers le haut principalement
            
            # Éviter les bords de la carte
            if self.position[0] < 100:  # Trop à gauche
                self.random_direction_x = abs(self.random_direction_x)
            elif self.position[0] > self.map_width - 100:  # Trop à droite
                self.random_direction_x = -abs(self.random_direction_x)
                
            if self.position[1] < 100:  # Trop en haut
                self.random_direction_y = abs(self.random_direction_y)
            elif self.position[1] > self.map_height - 100:  # Trop en bas
                self.random_direction_y = -abs(self.random_direction_y)

    def update_movement(self):
        """Met à jour le mouvement du bot allié"""
        # Calculer la direction cible
        self.target_x = self.position[0] + self.random_direction_x * 100
        self.target_y = self.position[1] + self.random_direction_y * 100
        
        # Calculer la direction vers la cible
        dx = self.target_x - self.position[0]
        dy = self.target_y - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:  # Si on n'est pas encore arrivé
            # Normaliser la direction
            dx /= distance
            dy /= distance
            
            # Appliquer l'accélération
            self.velocity_x += dx * self.acceleration
            self.velocity_y += dy * self.acceleration
            
            # Limiter la vitesse
            speed = math.sqrt(self.velocity_x*self.velocity_x + self.velocity_y*self.velocity_y)
            if speed > self.speed:
                self.velocity_x = (self.velocity_x / speed) * self.speed
                self.velocity_y = (self.velocity_y / speed) * self.speed
        
        # Appliquer la friction
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Mettre à jour la position
        self.position[0] += self.velocity_x
        self.position[1] += self.velocity_y
        
        # Garder dans les limites de la carte
        self.position[0] = max(32, min(self.map_width - 32, self.position[0]))
        self.position[1] = max(32, min(self.map_height - 32, self.position[1]))
        
        # Mettre à jour le rect
        self.rect.center = (int(self.position[0]), int(self.position[1]))
        
        # Déterminer la direction d'animation
        if abs(self.velocity_x) > abs(self.velocity_y):
            if self.velocity_x > 0:
                self.change_animation('right')
            else:
                self.change_animation('left')
        else:
            if self.velocity_y > 0:
                self.change_animation('down')
            else:
                self.change_animation('up')

    def update(self):
        """Mise à jour principale du bot allié"""
        self.update_random_movement()
        self.update_movement()
        
        # Animation
        if self.is_moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.current_direction]):
                self.frame_index = 0
            self.image = self.animations[self.current_direction][int(self.frame_index)]
        else:
            self.image = self.animations[self.current_direction][0]

    def get_position(self):
        """Retourne la position actuelle du bot allié"""
        return (self.position[0], self.position[1])