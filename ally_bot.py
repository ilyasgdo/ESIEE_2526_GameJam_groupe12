import pygame
import math
import random

class AllyBot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Utiliser le même sprite sheet que le joueur mais avec une couleur différente
        self.sprite_sheet = pygame.image.load('assets/sprites/player/RACCOONSPRITESHEET.png').convert_alpha()
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
        
        # Variables pour des mouvements plus naturels
        self.micro_movement_timer = 0
        self.micro_movement_x = 0
        self.micro_movement_y = 0
        self.hesitation_timer = 0
        self.is_hesitating = False
        self.natural_speed_variation = 1.0
        self.breathing_timer = 0
        
        # Limites de mouvement (pour rester dans les limites de la carte)
        self.map_width = 1280  # 40 * 32
        self.map_height = 6400  # 200 * 32
        
        # Récupérer toutes les frames (même système que le joueur)
        self.animations = {
            'down': self.load_row(5),
            'left': self.load_row(7),
            'right': self.load_row(9),
            'up': self.load_row(11)
        }
        
        # Appliquer une teinte verte pour distinguer le bot allié
        
        self.image = self.animations['up'][0]
        self.is_moving = True

    def get_image(self, x, y, scale=4):
        frame = pygame.Surface((32, 32), pygame.SRCALPHA)
        frame.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))

        # Agrandir la frame
        size = frame.get_width() * scale, frame.get_height() * scale
        frame = pygame.transform.scale(frame, size)
        return frame

    def load_row(self, row, scale=4):
        """Charge une ligne d'animation et scale chaque frame"""
        return [self.get_image(col * 32, row * 32, scale) for col in range(4)]

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
        """Met à jour le mouvement aléatoire avec tendance vers le haut et variations naturelles"""
        self.direction_change_timer += 1
        
        # Changer de direction aléatoirement avec variation
        base_interval = self.direction_change_interval
        if self.direction_change_timer >= base_interval:
            self.direction_change_timer = 0
            # Variation dans l'intervalle pour plus de naturel
            self.direction_change_interval = random.randint(40, 220)
            
            # Parfois hésiter avant de changer de direction
            if random.random() < 0.3:  # 30% de chance d'hésiter
                self.is_hesitating = True
                self.hesitation_timer = random.randint(10, 30)
                return
            
            # Mouvement aléatoire avec forte tendance vers le haut mais plus de variation
            self.random_direction_x = random.uniform(-0.7, 0.7)  # Plus de variation horizontale
            self.random_direction_y = random.uniform(-1.2, -0.1)  # Variation verticale
            
            # Ajouter des micro-corrections occasionnelles
            if random.random() < 0.4:  # 40% de chance
                self.random_direction_x += random.uniform(-0.3, 0.3)
                self.random_direction_y += random.uniform(-0.2, 0.2)
            
            # Éviter les bords de la carte avec plus de fluidité
            edge_buffer = 150  # Zone tampon plus large
            if self.position[0] < edge_buffer:  # Trop à gauche
                self.random_direction_x = abs(self.random_direction_x) + random.uniform(0.1, 0.3)
            elif self.position[0] > self.map_width - edge_buffer:  # Trop à droite
                self.random_direction_x = -abs(self.random_direction_x) - random.uniform(0.1, 0.3)
                
            if self.position[1] < edge_buffer:  # Trop en haut
                self.random_direction_y = abs(self.random_direction_y) + random.uniform(0.1, 0.3)
            elif self.position[1] > self.map_height - edge_buffer:  # Trop en bas
                self.random_direction_y = -abs(self.random_direction_y) - random.uniform(0.1, 0.3)
        
        # Gérer l'hésitation
        if self.is_hesitating:
            self.hesitation_timer -= 1
            if self.hesitation_timer <= 0:
                self.is_hesitating = False
            # Réduire le mouvement pendant l'hésitation
            self.natural_speed_variation = 0.3 + random.uniform(0, 0.4)
        else:
            # Variation naturelle de la vitesse
            self.natural_speed_variation = 0.8 + random.uniform(0, 0.4)
        
        # Micro-mouvements pour simuler l'imprécision naturelle
        self.micro_movement_timer += 1
        if self.micro_movement_timer >= 5:  # Chaque 5 frames
            self.micro_movement_timer = 0
            self.micro_movement_x = random.uniform(-0.1, 0.1)
            self.micro_movement_y = random.uniform(-0.1, 0.1)
        
        # Effet de "respiration" subtil
        self.breathing_timer += 0.1
        breathing_effect = math.sin(self.breathing_timer) * 0.05

    def update_movement(self):
        """Met à jour le mouvement du bot avec des transitions plus fluides"""
        # Calculer la direction vers la cible avec micro-mouvements
        target_direction_x = self.random_direction_x + self.micro_movement_x
        target_direction_y = self.random_direction_y + self.micro_movement_y
        
        # Ajouter l'effet de respiration
        breathing_effect = math.sin(self.breathing_timer) * 0.05
        target_direction_x += breathing_effect
        target_direction_y += breathing_effect * 0.5
        
        # Calculer la direction cible avec les effets naturels
        self.target_x = self.position[0] + target_direction_x * 100
        self.target_y = self.position[1] + target_direction_y * 100
        
        # Calculer la direction vers la cible
        dx = self.target_x - self.position[0]
        dy = self.target_y - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 5:  # Si on n'est pas encore arrivé
            # Normaliser la direction
            dx /= distance
            dy /= distance
            
            # Transition plus douce vers la nouvelle direction (interpolation)
            transition_speed = 0.15 if not self.is_hesitating else 0.05
            self.velocity_x += (dx * self.acceleration - self.velocity_x) * transition_speed
            self.velocity_y += (dy * self.acceleration - self.velocity_y) * transition_speed
            
            # Appliquer la variation de vitesse naturelle
            adjusted_speed = self.speed * self.natural_speed_variation
            
            # Limiter la vitesse avec une variation naturelle
            speed = math.sqrt(self.velocity_x*self.velocity_x + self.velocity_y*self.velocity_y)
            if speed > adjusted_speed:
                self.velocity_x = (self.velocity_x / speed) * adjusted_speed
                self.velocity_y = (self.velocity_y / speed) * adjusted_speed
        
        # Appliquer une friction variable pour plus de naturel
        friction_factor = self.friction + random.uniform(-0.02, 0.02)
        self.velocity_x *= friction_factor
        self.velocity_y *= friction_factor
        
        # Mettre à jour la position
        self.position[0] += self.velocity_x
        self.position[1] += self.velocity_y
        
        # Garder dans les limites de la carte
        self.position[0] = max(32, min(self.map_width - 32, self.position[0]))
        self.position[1] = max(32, min(self.map_height - 32, self.position[1]))
        
        # Mettre à jour le rect
        self.rect.center = (int(self.position[0]), int(self.position[1]))
        
        # Déterminer la direction d'animation avec plus de fluidité
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