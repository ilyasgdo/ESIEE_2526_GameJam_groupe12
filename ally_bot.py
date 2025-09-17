import pygame
import math
import random

class AllyBot(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        # Utiliser le même sprite sheet que le joueur mais avec une couleur différente
        self.sprite_sheet = pygame.image.load('assets/sprites/player/BIRDSPRITESHEET_Blue.png').convert_alpha()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.position = [float(x), float(y)]
        self.old_position = self.position.copy()  # Pour la gestion des collisions
        self.speed = 2.5  # Vitesse de déplacement
        self.frame_index = 0
        self.animation_speed = 1
        self.current_direction = 'down'
        
        # Référence au joueur (gardée pour la contrainte de distance du joueur)
        self.player = player
        
        # Système de checkpoints - Liste complète des positions à suivre
        self.checkpoints = [
            (459.67, 5933.67),
            (240.67, 5789.67),
            (300.67, 5588.67),
            (498.67, 5465.67),
            (729.67, 5441.67),
            (978.67, 5441.67),
            (1056.67, 5375.67),
            (1089.67, 5306.67),
            (1089.67, 5129.67),
            (903.67, 4997.67),
            (681.67, 4925.67),
            (555.67, 4787.67),
            (396.67, 4715.67),
            (321.67, 4640.67),
            (261.67, 4520.67),
            (360.67, 4301.67),
            (288.67, 4169.67),
            (288.67, 3911.67),
            (546.67, 3896.67),
            (831.67, 3896.67),
            (1059.67, 3896.67),
            (1059.67, 3749.67),
            (972.67, 3671.67),
            (906.67, 3596.67),
            (858.67, 3575.67),
            (798.67, 3527.67),
            (639.67, 3527.67),
            (402.67, 3527.67),
            (342.67, 3458.67),
            (261.67, 3404.67),
            (261.67, 3329.67),
            (261.67, 3248.67),
            (450.67, 3137.67),
            (645.67, 2987.67),
            (645.67, 2756.67),
            (645.67, 2543.67),
            (645.67, 2345.67),
            (579.67, 2180.67),
            (474.67, 2021.67),
            (327.67, 1793.67),
            (492.67, 1643.67),
            (618.67, 1499.67),
            (618.67, 1172.67),
            (348.67, 1007.67),
            (348.67, 800.67),
            (579.67, 530.67),
            (660.67, 272.67)
        ]
        self.current_checkpoint_index = 0
        self.checkpoint_reached_distance = 30  # Distance pour considérer qu'un checkpoint est atteint
        
        # Variables pour l'IA autonome avec checkpoints
        self.state = "moving_to_checkpoint"   # États: "moving_to_checkpoint", "pausing", "avoiding_bot"
        self.state_timer = 0
        self.pause_duration = 240  # 4 secondes à 60 FPS
        self.random_movement_timer = 0
        self.random_target_x = x
        self.random_target_y = y
        
        # Variables pour la détection du bot principal
        self.bot_detection_distance = 80  # Distance de détection du bot principal
        self.bot_avoidance_distance = 120  # Distance pour s'éloigner du bot
        self.bot_reference = None  # Sera défini plus tard
        
        # Variables pour mouvement fluide
        self.target_x = x
        self.target_y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.35
        self.friction = 0.88
        
        # Variables pour des mouvements plus naturels et réactifs
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
        
        # Appliquer une teinte différente pour distinguer le bot allié
        self.apply_tint((200, 255, 200))  # Teinte verte
        
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
        self.update_ai()
        self.update_movement()
        
        # Mettre à jour le rect
        self.rect.center = (int(self.position[0]), int(self.position[1]))
        
        # Déterminer la direction d'animation basée sur le mouvement
        movement_threshold = 0.2
        if abs(self.velocity_x) > movement_threshold or abs(self.velocity_y) > movement_threshold:
            self.is_moving = True
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
        else:
            self.is_moving = False
        
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

    def get_distance_to_checkpoint(self):
        """Calcule la distance au checkpoint actuel"""
        if self.current_checkpoint_index >= len(self.checkpoints):
            return 0  # Tous les checkpoints ont été atteints
        
        checkpoint = self.checkpoints[self.current_checkpoint_index]
        dx = self.position[0] - checkpoint[0]
        dy = self.position[1] - checkpoint[1]
        return math.sqrt(dx*dx + dy*dy)

    def get_distance_to_bot(self):
        """Calcule la distance au bot principal"""
        if not self.bot_reference:
            return float('inf')
        bot_pos = self.bot_reference.position
        dx = self.position[0] - bot_pos[0]
        dy = self.position[1] - bot_pos[1]
        return math.sqrt(dx*dx + dy*dy)

    def set_bot_reference(self, bot):
        """Définir la référence au bot principal pour la détection de proximité"""
        self.bot_reference = bot

    def update_ai(self):
        """Mise à jour de l'intelligence artificielle du bot avec système de checkpoints"""
        # Vérifier la proximité du bot principal
        distance_to_bot = self.get_distance_to_bot()
        
        if distance_to_bot < self.bot_detection_distance and self.state != "avoiding_bot":
            # Le bot principal est proche, passer en mode évitement
            self.state = "avoiding_bot"
            self.state_timer = 0
            
        elif distance_to_bot > self.bot_avoidance_distance and self.state == "avoiding_bot":
            # Le bot principal s'est éloigné, reprendre le mouvement normal
            self.state = "moving_to_checkpoint"
            self.state_timer = 0
        
        if self.state == "moving_to_checkpoint":
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
                
                # Passer en mode pause avec mouvements aléatoires
                self.state = "pausing"
                self.state_timer = 0
                self.set_random_pause_target()
            else:
                # Se diriger vers le checkpoint actuel
                self.target_x = current_checkpoint[0]
                self.target_y = current_checkpoint[1]
                
        elif self.state == "pausing":
            # Mode pause avec mouvements aléatoires pendant 4 secondes
            self.state_timer += 1
            
            # Changer de cible aléatoire toutes les 30 frames (0.5 seconde)
            if self.state_timer % 30 == 0:
                self.set_random_pause_target()
            
            # Fin de la pause après 4 secondes
            if self.state_timer >= self.pause_duration:
                self.state = "moving_to_checkpoint"
                self.state_timer = 0
                
        elif self.state == "avoiding_bot":
            # Mode évitement du bot principal - mouvement latéral aléatoire
            self.state_timer += 1
            
            # Changer de direction d'évitement toutes les 20 frames
            if self.state_timer % 20 == 0:
                self.set_avoidance_target()

    def set_random_pause_target(self):
        """Définir une cible aléatoire pour les mouvements pendant la pause"""
        # Mouvement aléatoire dans un petit rayon autour de la position actuelle
        pause_radius = 40
        angle = random.uniform(0, 2 * math.pi)
        self.random_target_x = self.position[0] + math.cos(angle) * random.uniform(10, pause_radius)
        self.random_target_y = self.position[1] + math.sin(angle) * random.uniform(10, pause_radius)
        self.target_x = self.random_target_x
        self.target_y = self.random_target_y

    def set_avoidance_target(self):
        """Définir une cible pour éviter le bot principal"""
        if not self.bot_reference:
            return
            
        # Calculer la direction opposée au bot principal
        bot_pos = self.bot_reference.position
        dx = self.position[0] - bot_pos[0]
        dy = self.position[1] - bot_pos[1]
        
        # Normaliser la direction
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Se déplacer dans la direction opposée avec un peu d'aléatoire
        avoidance_distance = 60
        angle_variation = random.uniform(-0.5, 0.5)  # Variation d'angle pour plus de naturel
        
        final_dx = dx * math.cos(angle_variation) - dy * math.sin(angle_variation)
        final_dy = dx * math.sin(angle_variation) + dy * math.cos(angle_variation)
        
        self.target_x = self.position[0] + final_dx * avoidance_distance
        self.target_y = self.position[1] + final_dy * avoidance_distance

    def get_distance_to_player(self):
        """Calculer la distance au joueur"""
        player_pos = self.player.position
        dx = player_pos[0] - self.position[0]
        dy = player_pos[1] - self.position[1]
        return math.sqrt(dx * dx + dy * dy)

    def get_angle_to_player(self):
        """Calculer l'angle vers le joueur"""
        player_pos = self.player.position
        dx = player_pos[0] - self.position[0]
        dy = player_pos[1] - self.position[1]
        return math.atan2(dy, dx)

    def update_movement(self):
        """Mise à jour du mouvement fluide vers la cible avec gestion des collisions"""
        # Sauvegarder la position actuelle
        self.save_position()
        
        # Micro-mouvements pour simuler l'imprécision naturelle
        self.micro_movement_timer += 1
        if self.micro_movement_timer >= random.randint(4, 8):  # Variation dans le timing
            self.micro_movement_timer = 0
            self.micro_movement_x = random.uniform(-0.1, 0.1)
            self.micro_movement_y = random.uniform(-0.1, 0.1)
        
        # Effet de "respiration" subtil
        self.breathing_timer += 0.08 + random.uniform(-0.01, 0.01)
        breathing_effect_x = math.sin(self.breathing_timer) * 0.05
        breathing_effect_y = math.cos(self.breathing_timer * 0.9) * 0.03
        
        # Calculer la direction vers la cible avec effets naturels
        adjusted_target_x = self.target_x + self.micro_movement_x + breathing_effect_x
        adjusted_target_y = self.target_y + self.micro_movement_y + breathing_effect_y
        
        dx = adjusted_target_x - self.position[0]
        dy = adjusted_target_y - self.position[1]
        distance_to_target = math.sqrt(dx*dx + dy*dy)
        
        # Hésitation occasionnelle lors de changements de direction
        if distance_to_target > 3:
            current_direction = math.atan2(dy, dx)
            if abs(current_direction - self.last_direction_change) > 0.3:
                if random.random() < 0.12 and not self.is_hesitating:  # 12% de chance
                    self.is_hesitating = True
                    self.hesitation_timer = random.randint(5, 12)
                    self.last_direction_change = current_direction
        
        # Gérer l'hésitation
        if self.is_hesitating:
            self.hesitation_timer -= 1
            if self.hesitation_timer <= 0:
                self.is_hesitating = False
            # Réduire le mouvement pendant l'hésitation
            self.natural_speed_variation = 0.5 + random.uniform(0, 0.3)
        else:
            # Variation naturelle de la vitesse
            base_variation = 0.9 + random.uniform(0, 0.3)
            # Ajuster selon la distance (plus loin = plus rapide)
            distance_factor = min(1.2, 0.95 + distance_to_target * 0.003)
            self.natural_speed_variation = base_variation * distance_factor
        
        # Appliquer l'accélération vers la cible avec transition douce
        acceleration_factor = self.acceleration * 0.01 * self.natural_speed_variation
        target_velocity_x = dx * acceleration_factor
        target_velocity_y = dy * acceleration_factor
        
        # Transition plus douce vers la nouvelle vélocité
        transition_speed = 0.12 if not self.is_hesitating else 0.04
        self.velocity_x += (target_velocity_x - self.velocity_x) * transition_speed
        self.velocity_y += (target_velocity_y - self.velocity_y) * transition_speed
        
        # Limiter la vitesse maximale avec variation naturelle
        current_max_speed = self.speed * (0.9 + random.uniform(0, 0.2))
        speed = math.sqrt(self.velocity_x * self.velocity_x + self.velocity_y * self.velocity_y)
        if speed > current_max_speed:
            self.velocity_x = (self.velocity_x / speed) * current_max_speed
            self.velocity_y = (self.velocity_y / speed) * current_max_speed
        
        # Appliquer une friction variable
        friction_factor = self.friction + random.uniform(-0.015, 0.015)
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
                pass