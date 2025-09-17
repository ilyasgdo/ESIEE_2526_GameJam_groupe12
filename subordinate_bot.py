import pygame
import math
import random

class SubordinateBot(pygame.sprite.Sprite):
    def __init__(self, x, y, leader, formation_angle, formation_radius=60):
        super().__init__()
        # Utiliser le même sprite sheet que le joueur mais avec une couleur différente
        self.sprite_sheet = pygame.image.load('assets/sprites/player/BIRDSPRITESHEET_Blue.png').convert_alpha()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.position = [float(x), float(y)]
        self.speed = 1.8  # Légèrement plus rapide pour rattraper le leader
        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_direction = 'up'
        
        # Référence au leader (AllyBot)
        self.leader = leader
        
        # Variables de formation
        self.formation_angle = formation_angle  # Angle en radians pour la position dans la formation
        self.formation_radius = formation_radius  # Distance du leader
        self.target_position = [x, y]  # Position cible dans la formation
        
        # Variables pour mouvement fluide
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.3
        self.friction = 0.85
        self.max_speed = 3.0
        
        # Variables pour éviter les collisions entre subordonnés
        self.separation_radius = 25
        self.cohesion_strength = 0.1
        self.separation_strength = 0.5
        
        # Récupérer toutes les frames (même système que le joueur)
        self.animations = {
            'down': self.load_row(0),
            'left': self.load_row(2),
            'right': self.load_row(1),
            'up': self.load_row(3)
        }
        
        # Appliquer une teinte bleue pour distinguer les subordonnés
        self.apply_tint((150, 200, 255))  # Teinte bleue
        
        self.image = self.animations['up'][0]
        self.is_moving = True

    def get_image(self, x, y):
        """Récupère une image du sprite sheet"""
        image = pygame.Surface((32, 32), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image

    def load_row(self, row):
        """Charge une ligne complète d'animations"""
        return [self.get_image(x * 32, row * 32) for x in range(4)]

    def apply_tint(self, color):
        """Applique une teinte colorée aux animations"""
        for direction in self.animations:
            for i, frame in enumerate(self.animations[direction]):
                # Créer une surface avec la teinte
                tinted_frame = frame.copy()
                tint_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
                tint_surface.fill(color + (100,))  # Alpha de 100 pour la teinte
                tinted_frame.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                self.animations[direction][i] = tinted_frame

    def change_animation(self, direction):
        """Change la direction de l'animation"""
        if direction != self.current_direction:
            self.current_direction = direction
            self.frame_index = 0

    def calculate_formation_position(self):
        """Calcule la position cible dans la formation autour du leader"""
        if not self.leader:
            return self.position
        
        leader_pos = self.leader.get_position()
        
        # Calculer la position cible en formation circulaire
        target_x = leader_pos[0] + math.cos(self.formation_angle) * self.formation_radius
        target_y = leader_pos[1] + math.sin(self.formation_angle) * self.formation_radius
        
        return [target_x, target_y]

    def update_formation_movement(self, subordinates_list):
        """Met à jour le mouvement pour maintenir la formation"""
        if not self.leader:
            return
        
        # Calculer la position cible dans la formation
        self.target_position = self.calculate_formation_position()
        
        # Calculer la direction vers la position cible
        dx = self.target_position[0] - self.position[0]
        dy = self.target_position[1] - self.position[1]
        distance_to_target = math.sqrt(dx*dx + dy*dy)
        
        # Force d'attraction vers la position de formation
        if distance_to_target > 5:  # Seuil minimum pour éviter les oscillations
            force_x = (dx / distance_to_target) * self.acceleration
            force_y = (dy / distance_to_target) * self.acceleration
        else:
            force_x = force_y = 0
        
        # Force de séparation avec les autres subordonnés
        separation_x, separation_y = self.calculate_separation(subordinates_list)
        
        # Appliquer les forces
        self.velocity_x += force_x + separation_x * self.separation_strength
        self.velocity_y += force_y + separation_y * self.separation_strength
        
        # Appliquer la friction
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Limiter la vitesse maximale
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed > self.max_speed:
            self.velocity_x = (self.velocity_x / speed) * self.max_speed
            self.velocity_y = (self.velocity_y / speed) * self.max_speed
        
        # Mettre à jour la position
        self.position[0] += self.velocity_x
        self.position[1] += self.velocity_y
        
        # Déterminer la direction d'animation
        if abs(self.velocity_x) > abs(self.velocity_y):
            if self.velocity_x > 0.1:
                self.change_animation('right')
            elif self.velocity_x < -0.1:
                self.change_animation('left')
        else:
            if self.velocity_y > 0.1:
                self.change_animation('down')
            elif self.velocity_y < -0.1:
                self.change_animation('up')
        
        # Déterminer si le bot bouge
        self.is_moving = speed > 0.1

    def calculate_separation(self, subordinates_list):
        """Calcule la force de séparation avec les autres subordonnés"""
        separation_x = 0
        separation_y = 0
        
        for other in subordinates_list:
            if other == self:
                continue
            
            dx = self.position[0] - other.position[0]
            dy = self.position[1] - other.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < self.separation_radius and distance > 0:
                # Force inversement proportionnelle à la distance
                force = (self.separation_radius - distance) / self.separation_radius
                separation_x += (dx / distance) * force
                separation_y += (dy / distance) * force
        
        return separation_x, separation_y

    def update(self, subordinates_list=None):
        """Met à jour le subordonné"""
        # Mettre à jour le mouvement de formation
        if subordinates_list is None:
            subordinates_list = []
        self.update_formation_movement(subordinates_list)
        
        # Mettre à jour la position du rectangle
        self.rect.topleft = self.position
        
        # Mettre à jour l'animation
        if self.is_moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.current_direction]):
                self.frame_index = 0
            self.image = self.animations[self.current_direction][int(self.frame_index)]
        else:
            self.image = self.animations[self.current_direction][0]

    def get_position(self):
        """Retourne la position actuelle du subordonné"""
        return (self.position[0], self.position[1])