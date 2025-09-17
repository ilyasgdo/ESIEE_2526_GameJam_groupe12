import pygame
import math
import random

class Bot(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        # Utiliser le même sprite sheet que le joueur mais avec une couleur différente
        self.sprite_sheet = pygame.image.load('assets/sprites/player/BIRDSPRITESHEET_Blue.png').convert_alpha()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.position = [float(x), float(y)]
        self.speed = 2  # Légèrement plus lent que le joueur
        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_direction = 'down'
        
        # Référence au joueur à suivre
        self.player = player
        
        # Variables pour l'IA de suivi et rotation
        self.follow_distance = 80  # Distance à maintenir avec le joueur
        self.orbit_radius = 60     # Rayon de l'orbite autour du joueur
        self.orbit_angle = random.uniform(0, 2 * math.pi)  # Angle initial aléatoire
        self.orbit_speed = 0.02    # Vitesse de rotation autour du joueur
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

    def get_distance_to_player(self):
        """Calculer la distance au joueur"""
        dx = self.player.position[0] - self.position[0]
        dy = self.player.position[1] - self.position[1]
        return math.sqrt(dx * dx + dy * dy)

    def get_angle_to_player(self):
        """Calculer l'angle vers le joueur"""
        dx = self.player.position[0] - self.position[0]
        dy = self.player.position[1] - self.position[1]
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
                self.orbit_angle = self.get_angle_to_player()
            else:
                self.state = "following"
        
        distance_to_player = self.get_distance_to_player()
        
        if self.state == "following":
            # Comportement de suivi
            if distance_to_player > self.follow_distance:
                # Se rapprocher du joueur
                angle = self.get_angle_to_player()
                self.target_x = self.player.position[0] - math.cos(angle) * (self.follow_distance * 0.8)
                self.target_y = self.player.position[1] - math.sin(angle) * (self.follow_distance * 0.8)
            else:
                # Rester à distance
                angle = self.get_angle_to_player()
                self.target_x = self.player.position[0] - math.cos(angle) * self.follow_distance
                self.target_y = self.player.position[1] - math.sin(angle) * self.follow_distance
                
        elif self.state == "orbiting":
            # Comportement d'orbite autour du joueur
            self.orbit_angle += self.orbit_speed
            if self.orbit_angle > 2 * math.pi:
                self.orbit_angle -= 2 * math.pi
                
            self.target_x = self.player.position[0] + math.cos(self.orbit_angle) * self.orbit_radius
            self.target_y = self.player.position[1] + math.sin(self.orbit_angle) * self.orbit_radius

    def update_movement(self):
        """Mise à jour du mouvement fluide vers la cible"""
        # Calculer la direction vers la cible
        dx = self.target_x - self.position[0]
        dy = self.target_y - self.position[1]
        
        # Appliquer l'accélération vers la cible
        self.velocity_x += dx * self.acceleration * 0.01
        self.velocity_y += dy * self.acceleration * 0.01
        
        # Limiter la vitesse maximale
        max_speed = self.speed
        speed = math.sqrt(self.velocity_x * self.velocity_x + self.velocity_y * self.velocity_y)
        if speed > max_speed:
            self.velocity_x = (self.velocity_x / speed) * max_speed
            self.velocity_y = (self.velocity_y / speed) * max_speed
        
        # Appliquer la friction
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Mettre à jour la position
        self.position[0] += self.velocity_x
        self.position[1] += self.velocity_y
        
        # Déterminer la direction d'animation basée sur le mouvement
        if abs(self.velocity_x) > abs(self.velocity_y):
            if self.velocity_x > 0.5:
                self.change_animation('right')
                self.is_moving = True
            elif self.velocity_x < -0.5:
                self.change_animation('left')
                self.is_moving = True
            else:
                self.is_moving = False
        else:
            if self.velocity_y > 0.5:
                self.change_animation('down')
                self.is_moving = True
            elif self.velocity_y < -0.5:
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