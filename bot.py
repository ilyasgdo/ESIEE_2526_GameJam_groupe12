import pygame
import math
import random

class Bot(pygame.sprite.Sprite):
    def __init__(self, x, y, ally_bot):
        super().__init__()
        # Utiliser le même sprite sheet que le joueur mais avec une couleur différente
        self.sprite_sheet = pygame.image.load('assets/sprites/player/BIRDSPRITESHEET_Blue.png').convert_alpha()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.position = [float(x), float(y)]
        self.speed = 2  # Légèrement plus lent que le joueur
        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_direction = 'down'
        
        # Référence au bot allié à suivre (au lieu du joueur)
        self.ally_bot = ally_bot
        
        # Variables pour l'IA de suivi et rotation
        self.follow_distance = 80  # Distance à maintenir avec le bot allié
        self.orbit_radius = 60     # Rayon de l'orbite autour du bot allié
        self.orbit_angle = random.uniform(0, 2 * math.pi)  # Angle initial aléatoire
        self.orbit_speed = 0.02    # Vitesse de rotation autour du bot allié
        self.state = "following"   # États: "following", "orbiting"
        self.state_timer = 0
        self.state_change_interval = 180  # Changer d'état toutes les 3 secondes (60 FPS)
        
        # Variables pour mouvement fluide
        self.target_x = x
        self.target_y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.3
        self.friction = 0.85
        
        # Variables pour des mouvements plus naturels
        self.micro_movement_timer = 0
        self.micro_movement_x = 0
        self.micro_movement_y = 0
        self.hesitation_timer = 0
        self.is_hesitating = False
        self.natural_speed_variation = 1.0
        self.breathing_timer = 0
        self.last_direction_change = 0
        
        # Récupérer toutes les frames (même système que le joueur)
        self.animations = {
            'down': self.load_row(0),
            'left': self.load_row(2),
            'right': self.load_row(1),
            'up': self.load_row(3)
        }
        
        # Appliquer une teinte différente pour distinguer le bot
        self.apply_tint((255, 200, 200))  # Teinte rosée
        
        self.image = self.animations['down'][0]
        self.is_moving = False

    def get_image(self, x, y):
        """Extraire une image du sprite sheet"""
        image = pygame.Surface((32, 32), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image

    def load_row(self, row):
        """Charge une ligne de 4 frames à partir du sprite sheet"""
        return [self.get_image(col * 32, row * 32) for col in range(4)]
    
    def apply_tint(self, color):
        """Appliquer une teinte colorée aux animations pour différencier le bot"""
        for direction in self.animations:
            for i, frame in enumerate(self.animations[direction]):
                # Créer une surface avec la teinte
                tinted_frame = frame.copy()
                tint_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
                tint_surface.fill((*color, 100))  # Alpha de 100 pour un effet subtil
                tinted_frame.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                self.animations[direction][i] = tinted_frame

    def change_animation(self, direction):
        """Changer la direction d'animation"""
        if self.current_direction != direction:
            self.current_direction = direction
            self.frame_index = 0

    def get_distance_to_ally(self):
        """Calcule la distance au bot allié"""
        if not self.ally_bot:
            return float('inf')
        ally_pos = self.ally_bot.get_position()
        dx = self.position[0] - ally_pos[0]
        dy = self.position[1] - ally_pos[1]
        return math.sqrt(dx*dx + dy*dy)

    def get_angle_to_ally(self):
        """Calcule l'angle vers le bot allié"""
        if not self.ally_bot:
            return 0
        ally_pos = self.ally_bot.get_position()
        dx = ally_pos[0] - self.position[0]
        dy = ally_pos[1] - self.position[1]
        return math.atan2(dy, dx)

    def update_ai(self):
        """Mise à jour de l'intelligence artificielle du bot"""
        self.state_timer += 1
        
        # Changer d'état périodiquement
        if self.state_timer >= self.state_change_interval:
            self.state_timer = 0
            if self.state == "following":
                self.state = "orbiting"
                # Calculer l'angle initial pour l'orbite
                self.orbit_angle = self.get_angle_to_ally()
            else:
                self.state = "following"
        
        distance_to_ally = self.get_distance_to_ally()
        
        if self.state == "following":
            # Comportement de suivi du bot allié
            if distance_to_ally > self.follow_distance:
                # Se rapprocher du bot allié
                angle = self.get_angle_to_ally()
                ally_pos = self.ally_bot.get_position()
                self.target_x = ally_pos[0] - math.cos(angle) * (self.follow_distance * 0.8)
                self.target_y = ally_pos[1] - math.sin(angle) * (self.follow_distance * 0.8)
            else:
                # Rester à distance du bot allié
                angle = self.get_angle_to_ally()
                ally_pos = self.ally_bot.get_position()
                self.target_x = ally_pos[0] - math.cos(angle) * self.follow_distance
                self.target_y = ally_pos[1] - math.sin(angle) * self.follow_distance
                
        elif self.state == "orbiting":
            # Comportement d'orbite autour du bot allié
            self.orbit_angle += self.orbit_speed
            if self.orbit_angle > 2 * math.pi:
                self.orbit_angle -= 2 * math.pi
            
            ally_pos = self.ally_bot.get_position()
            self.target_x = ally_pos[0] + math.cos(self.orbit_angle) * self.orbit_radius
            self.target_y = ally_pos[1] + math.sin(self.orbit_angle) * self.orbit_radius

    def update_movement(self):
        """Mise à jour du mouvement fluide vers la cible avec des comportements naturels"""
        # Micro-mouvements pour simuler l'imprécision naturelle
        self.micro_movement_timer += 1
        if self.micro_movement_timer >= random.randint(4, 10):  # Variation dans le timing
            self.micro_movement_timer = 0
            self.micro_movement_x = random.uniform(-0.12, 0.12)
            self.micro_movement_y = random.uniform(-0.12, 0.12)
        
        # Effet de "respiration" subtil
        self.breathing_timer += 0.06 + random.uniform(-0.01, 0.01)
        breathing_effect_x = math.sin(self.breathing_timer) * 0.06
        breathing_effect_y = math.cos(self.breathing_timer * 0.8) * 0.04
        
        # Calculer la direction vers la cible avec effets naturels
        adjusted_target_x = self.target_x + self.micro_movement_x + breathing_effect_x
        adjusted_target_y = self.target_y + self.micro_movement_y + breathing_effect_y
        
        dx = adjusted_target_x - self.position[0]
        dy = adjusted_target_y - self.position[1]
        distance_to_target = math.sqrt(dx*dx + dy*dy)
        
        # Hésitation occasionnelle lors de changements de direction
        if distance_to_target > 3:
            current_direction = math.atan2(dy, dx)
            if abs(current_direction - self.last_direction_change) > 0.4:
                if random.random() < 0.15 and not self.is_hesitating:  # 15% de chance
                    self.is_hesitating = True
                    self.hesitation_timer = random.randint(6, 15)
                    self.last_direction_change = current_direction
        
        # Gérer l'hésitation
        if self.is_hesitating:
            self.hesitation_timer -= 1
            if self.hesitation_timer <= 0:
                self.is_hesitating = False
            # Réduire le mouvement pendant l'hésitation
            self.natural_speed_variation = 0.4 + random.uniform(0, 0.3)
        else:
            # Variation naturelle de la vitesse
            base_variation = 0.8 + random.uniform(0, 0.4)
            # Ajuster selon la distance (plus loin = plus rapide)
            distance_factor = min(1.1, 0.9 + distance_to_target * 0.005)
            self.natural_speed_variation = base_variation * distance_factor
        
        # Appliquer l'accélération vers la cible avec transition douce
        acceleration_factor = self.acceleration * 0.01 * self.natural_speed_variation
        target_velocity_x = dx * acceleration_factor
        target_velocity_y = dy * acceleration_factor
        
        # Transition plus douce vers la nouvelle vélocité
        transition_speed = 0.1 if not self.is_hesitating else 0.03
        self.velocity_x += (target_velocity_x - self.velocity_x) * transition_speed
        self.velocity_y += (target_velocity_y - self.velocity_y) * transition_speed
        
        # Limiter la vitesse maximale avec variation naturelle
        current_max_speed = self.speed * (0.85 + random.uniform(0, 0.3))
        speed = math.sqrt(self.velocity_x * self.velocity_x + self.velocity_y * self.velocity_y)
        if speed > current_max_speed:
            self.velocity_x = (self.velocity_x / speed) * current_max_speed
            self.velocity_y = (self.velocity_y / speed) * current_max_speed
        
        # Appliquer une friction variable
        friction_factor = self.friction + random.uniform(-0.02, 0.02)
        self.velocity_x *= friction_factor
        self.velocity_y *= friction_factor
        
        # Mettre à jour la position
        self.position[0] += self.velocity_x
        self.position[1] += self.velocity_y
        
        # Déterminer la direction d'animation basée sur le mouvement avec plus de fluidité
        movement_threshold = 0.3  # Seuil plus bas pour plus de réactivité
        if abs(self.velocity_x) > abs(self.velocity_y):
            if self.velocity_x > movement_threshold:
                self.change_animation('right')
                self.is_moving = True
            elif self.velocity_x < -movement_threshold:
                self.change_animation('left')
                self.is_moving = True
            else:
                self.is_moving = False
        else:
            if self.velocity_y > movement_threshold:
                self.change_animation('down')
                self.is_moving = True
            elif self.velocity_y < -movement_threshold:
                self.change_animation('up')
                self.is_moving = True
            else:
                self.is_moving = False

    def update(self):
        """Mise à jour principale du bot"""
        # Mise à jour de l'IA
        self.update_ai()
        
        # Mise à jour du mouvement
        self.update_movement()
        
        # Mise à jour de la position du rect
        self.rect.topleft = (int(self.position[0]), int(self.position[1]))
        
        # Mise à jour de l'animation
        if self.is_moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.current_direction]):
                self.frame_index = 0
            self.image = self.animations[self.current_direction][int(self.frame_index)]
        else:
            self.image = self.animations[self.current_direction][0]