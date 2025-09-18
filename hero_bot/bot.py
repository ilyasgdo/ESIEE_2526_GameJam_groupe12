import pygame
import math
import random

from actions.actions import check_trap


class Bot(pygame.sprite.Sprite):
    def __init__(self, x, y, ally_bot, game_manager):
        super().__init__()
        # Utiliser le même sprite sheet que le joueur mais avec une couleur différente
        self.sprite_sheet = pygame.image.load('assets/sprites/player/Hero.png').convert_alpha()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.position = [float(x), float(y)]
        self.old_position = self.position.copy()  # Pour la gestion des collisions
        self.speed = 3 # Légèrement plus lent que le joueur
        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_direction = 'down'
        self.game_manager = game_manager
        
        # Référence au bot allié à suivre (au lieu du joueur)
        self.ally_bot = ally_bot
        
        # Système de checkpoints - Nouvelle liste de positions du joueur
        self.checkpoints = [
            (624.67, 6317.67),
            (789.67, 6317.67),
            (921.67, 6317.67),
            (954.67, 6317.67),
            (954.67, 6035.67),
            (873.67, 5999.67),
            (873.67, 6041.67),
            (813.67, 6071.67),
            (687.67, 6071.67),
            (606.67, 6071.67),
            (606.67, 5999.67),
            (552.67, 5999.67),
            (507.67, 5942.67),
            (360.67, 5942.67),
            (270.67, 5870.67),
            (225.67, 5756.67),
            (258.67, 5636.67),
            (336.67, 5567.67),
            (432.67, 5489.67),
            (552.67, 5456.67),
            (663.67, 5456.67),
            (804.67, 5456.67),
            (927.67, 5456.67),
            (972.67, 5381.67),
            (1083.67, 5330.67),
            (1083.67, 5165.67),
            (993.67, 5033.67),
            (915.67, 4958.67),
            (762.67, 4934.67),
            (672.67, 4889.67),
            (621.67, 4811.67),
            (522.67, 4745.67),
            (411.67, 4616.67),
            (333.67, 4532.67),
            (333.67, 4361.67),
            (333.67, 4190.67),
            (291.67, 4067.67),
            (291.67, 3983.67),
            (291.67, 3914.67),
            (408.67, 3914.67),
            (510.67, 3863.67),
            (609.67, 3863.67),
            (702.67, 3863.67),
            (702.67, 3911.67),
            (846.67, 3911.67),
            (990.67, 3911.67),
            (1044.67, 3911.67),
            (1092.67, 3761.67),
            (984.67, 3629.67),
            (882.67, 3566.67),
            (795.67, 3536.67),
            (669.67, 3536.67),
            (483.67, 3536.67),
            (363.67, 3500.67),
            (297.67, 3440.67),
            (258.67, 3311.67),
            (339.67, 3197.67),
            (468.67, 3101.67),
            (606.67, 3023.67),
            (681.67, 2915.67),
            (681.67, 2777.67),
            (639.67, 2585.67),
            (603.67, 2408.67),
            (603.67, 2234.67),
            (561.67, 2069.67),
            (363.67, 1994.67),
            (264.67, 1859.67),
            (264.67, 1748.67),
            (354.67, 1748.67),
            (432.67, 1631.67),
            (561.67, 1565.67),
            (624.67, 1481.67),
            (624.67, 1367.67),
            (624.67, 1220.67),
            (876.67, 1028.67),
            (933.67, 908.67),
            (858.67, 824.67),
            (612.67, 791.67),
            (612.67, 650.67),
            (612.67, 440.67),
            (612.67, 323.67)
        ]
        self.current_checkpoint_index = 0
        self.checkpoint_reached_distance = 50  # Distance pour considérer qu'un checkpoint est atteint
        self.state = "checkpoint_following"  # Nouvel état pour suivre les checkpoints
        
        # Variables pour l'IA de suivi et rotation (gardées pour compatibilité)
        self.follow_distance = 80  # Distance à maintenir avec le bot allié
        self.orbit_radius = 45     # Rayon de l'orbite autour du bot allié (réduit pour plus de proximité)
        self.orbit_angle = random.uniform(0, 2 * math.pi)  # Angle initial aléatoire
        self.orbit_speed = 0.04    # Vitesse de rotation autour du bot allié (augmentée pour plus de dynamisme)
        self.state_timer = 0
        self.state_change_interval = 180  # Changer d'état toutes les 3 secondes (60 FPS)
        
        # Nouveaux timers pour le comportement temporisé
        self.orbit_duration = 600  # 10 secondes à 60 FPS (10 * 60)
        self.wait_duration = 600   # 10 secondes d'attente à 60 FPS (10 * 60)
        self.orbit_timer = 0       # Timer pour compter le temps d'orbite
        self.wait_timer = 0        # Timer pour compter le temps d'attente
        
        # Variables pour mouvement fluide
        self.target_x = x
        self.target_y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.75  # Augmenté de 0.3 à 1.5
        self.friction = 0.95     # Augmenté de 0.85 à 0.95 (moins de friction)
        
        # Variables pour des mouvements plus naturels
        self.micro_movement_timer = 0
        self.micro_movement_x = 0
        self.micro_movement_y = 0
        self.hesitation_timer = 0
        self.is_hesitating = False
        self.natural_speed_variation = 1.0
        self.breathing_timer = 0
        self.last_direction_change = 0
        
        # Système de collision avec les objets TMX
        self.collision_objects = []
        
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

    def set_collision_objects(self, collision_objects):
        """Définir les objets de collision TMX"""
        self.collision_objects = collision_objects

    def save_position(self):
        """Sauvegarder la position actuelle pour pouvoir revenir en arrière en cas de collision"""
        self.old_position = self.position.copy()

    def restore_position(self):
        """Restaurer la position précédente en cas de collision"""
        self.position = self.old_position.copy()
        self.rect.topleft = self.position

    def check_collision_with_rect(self, rect):
        """Vérifier la collision avec un rectangle donné"""
        return (self.position[0] >= rect.x and self.position[1] >= rect.y and
                self.position[0] <= rect.x + rect.width and self.position[1] <= rect.y + rect.height)

    def check_collision_at_position(self, x, y):
        """Vérifier s'il y a collision à une position donnée"""
        for obj in self.collision_objects:
            if (x >= obj.x and y >= obj.y and
                x <= obj.x + obj.width and y <= obj.y + obj.height):
                return True
        return False

    def can_move_to(self, new_x, new_y):
        """Vérifier si le bot peut se déplacer à la position donnée"""
        return not self.check_collision_at_position(new_x, new_y)

    def get_image(self, x, y, scale=2):
        """Extraire une image du sprite sheet"""
        frame = pygame.Surface((32, 32), pygame.SRCALPHA)
        frame.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        # Agrandir la frame
        size = frame.get_width() * scale, frame.get_height() * scale
        frame = pygame.transform.scale(frame, size)
        return frame

    def load_row(self, row, scale=2):
        """Charge une ligne d'animation et scale chaque frame"""
        return [self.get_image(col * 32, row * 32, scale) for col in range(4)]
    
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

    def get_distance_to_checkpoint(self):
        """Calcule la distance au checkpoint actuel"""
        if self.current_checkpoint_index >= len(self.checkpoints):
            return 0  # Tous les checkpoints ont été atteints
        
        checkpoint = self.checkpoints[self.current_checkpoint_index]
        dx = self.position[0] - checkpoint[0]
        dy = self.position[1] - checkpoint[1]
        return math.sqrt(dx*dx + dy*dy)

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
        # Vérifier d'abord la proximité avec l'ally bot
        distance_to_ally = self.get_distance_to_ally()
        
        # Si l'ally bot est proche (moins de 100 pixels), passer en mode orbite
        if distance_to_ally < 100 and self.ally_bot:
            if self.state != "orbiting" and self.state != "waiting":
                self.state = "orbiting"
                self.orbit_angle = self.get_angle_to_ally()
                self.orbit_timer = 0  # Réinitialiser le timer d'orbite
        # Si l'ally bot est loin (plus de 150 pixels), retourner au suivi des checkpoints
        elif distance_to_ally > 150 or not self.ally_bot:
            if self.state != "checkpoint_following":
                self.state = "checkpoint_following"
                self.orbit_timer = 0
                self.wait_timer = 0
        
        if self.state == "checkpoint_following":
            # Vérifier si tous les checkpoints ont été atteints
            if self.current_checkpoint_index >= len(self.checkpoints):
                # Recommencer depuis le premier checkpoint
                self.current_checkpoint_index = 0
            
            # Obtenir le checkpoint actuel
            current_checkpoint = self.checkpoints[self.current_checkpoint_index]
            distance_to_checkpoint = self.get_distance_to_checkpoint()
            
            # Vérifier si le checkpoint actuel est atteint
            if distance_to_checkpoint <= self.checkpoint_reached_distance:
                self.current_checkpoint_index += 1
            
            # Définir la cible comme le checkpoint actuel
            if self.current_checkpoint_index < len(self.checkpoints):
                self.target_x = current_checkpoint[0]
                self.target_y = current_checkpoint[1]
        
        elif self.state == "orbiting":
            # Comportement d'orbite autour du bot allié avec timer
            self.orbit_timer += 1
            
            # Si on a orbitté pendant 10 secondes, passer en mode attente
            if self.orbit_timer >= self.orbit_duration:
                self.state = "waiting"
                self.wait_timer = 0
                # Arrêter le mouvement pendant l'attente
                self.target_x = self.rect.centerx
                self.target_y = self.rect.centery
            else:
                # Continuer l'orbite
                self.orbit_angle += self.orbit_speed
                if self.orbit_angle > 2 * math.pi:
                    self.orbit_angle -= 2 * math.pi
                
                ally_pos = self.ally_bot.get_position()
                self.target_x = ally_pos[0] + math.cos(self.orbit_angle) * self.orbit_radius
                self.target_y = ally_pos[1] + math.sin(self.orbit_angle) * self.orbit_radius
        
        elif self.state == "waiting":
            # État d'attente de 10 secondes
            self.wait_timer += 1
            
            # Rester immobile pendant l'attente
            self.target_x = self.rect.centerx
            self.target_y = self.rect.centery
            
            # Si on a attendu 10 secondes, retourner au suivi des checkpoints
            if self.wait_timer >= self.wait_duration:
                self.state = "checkpoint_following"
                self.orbit_timer = 0
                self.wait_timer = 0
                
                # Retourner à deux checkpoints en arrière
                self.current_checkpoint_index = max(0, self.current_checkpoint_index - 2)
        
        else:
            # Ancien comportement de suivi de l'ally bot (gardé pour compatibilité si nécessaire)
            pass

    def update_movement(self):
        """Mise à jour du mouvement fluide vers la cible avec des comportements naturels"""
        # Sauvegarder la position actuelle
        self.save_position()
        
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
            base_variation = 1.0 + random.uniform(0, 0.2)  # Augmenté de 0.8-1.2 à 1.0-1.2
            # Ajuster selon la distance (plus loin = plus rapide)
            distance_factor = min(1.3, 1.0 + distance_to_target * 0.008)  # Augmenté les facteurs
            self.natural_speed_variation = base_variation * distance_factor
        
        # Appliquer l'accélération vers la cible avec transition douce
        acceleration_factor = self.acceleration * 0.05 * self.natural_speed_variation  # Augmenté de 0.01 à 0.05
        target_velocity_x = dx * acceleration_factor
        target_velocity_y = dy * acceleration_factor
        
        # Transition plus douce vers la nouvelle vélocité
        transition_speed = 0.1 if not self.is_hesitating else 0.03
        self.velocity_x += (target_velocity_x - self.velocity_x) * transition_speed
        self.velocity_y += (target_velocity_y - self.velocity_y) * transition_speed
        
        # Limiter la vitesse maximale avec variation naturelle
        current_max_speed = self.speed * (1.0 + random.uniform(0, 0.2))  # Augmenté de 0.85-1.15 à 1.0-1.2
        speed = math.sqrt(self.velocity_x * self.velocity_x + self.velocity_y * self.velocity_y)
        if speed > current_max_speed:
            self.velocity_x = (self.velocity_x / speed) * current_max_speed
            self.velocity_y = (self.velocity_y / speed) * current_max_speed
        
        # Appliquer une friction variable
        friction_factor = self.friction + random.uniform(-0.02, 0.02)
        self.velocity_x *= friction_factor
        self.velocity_y *= friction_factor
        
        # Calculer la nouvelle position
        new_x = self.position[0] + self.velocity_x
        new_y = self.position[1] + self.velocity_y
        
        # Vérifier les collisions avant de mettre à jour la position
        if self.can_move_to(new_x, new_y):
            # Pas de collision, mettre à jour la position
            self.position[0] = new_x
            self.position[1] = new_y
        else:
            # Collision détectée, essayer de se déplacer sur un seul axe
            if self.can_move_to(new_x, self.position[1]):
                # Mouvement horizontal possible
                self.position[0] = new_x
            elif self.can_move_to(self.position[0], new_y):
                # Mouvement vertical possible
                self.position[1] = new_y
            else:
                # Aucun mouvement possible, restaurer la position
                self.restore_position()

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
        check_trap(self)
        
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