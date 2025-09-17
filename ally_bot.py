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
        
        # Système de checkpoints avec les positions fournies
        self.checkpoints = [
            (843.67, 6017.67),
            (594.67, 6077.67),
            (594.67, 5978.67),
            (291.67, 5978.67),
            (234.67, 5750.67),
            (351.67, 5561.67),
            (498.67, 5465.67),
            (996.67, 5465.67),
            (1077.67, 5294.67),
            (1077.67, 5096.67),
            (666.67, 4886.67),
            (339.67, 4586.67),
            (261.67, 3977.67),
            (660.67, 3884.67),
            (1026.67, 3893.67),
            (1086.67, 3725.67),
            (795.67, 3521.67),
            (369.67, 3470.67),
            (288.67, 3269.67),
            (558.67, 3035.67),
            (678.67, 2675.67),
            (678.67, 2354.67)
        ]
        self.current_checkpoint_index = 0
        self.checkpoint_reached_distance = 50  # Distance pour considérer qu'un checkpoint est atteint
        
        # Variables pour les pauses aux checkpoints
        self.is_pausing = False
        self.pause_timer = 0
        self.pause_duration = 240  # 4 secondes à 60 FPS
        self.random_movement_timer = 0
        self.random_movement_interval = 15  # Changer de direction aléatoire toutes les 0.25 secondes
        self.random_target_x = x
        self.random_target_y = y
        
        # Variables pour la détection de proximité avec le bot principal
        self.bot_reference = None  # Sera défini plus tard
        self.proximity_distance = 80  # Distance de proximité avec le bot principal
        self.is_near_bot = False
        self.near_bot_timer = 0
        self.near_bot_movement_timer = 0
        
        # Variables pour l'IA autonome (gardées pour compatibilité)
        self.state = "checkpoint_following"   # Nouvel état pour suivre les checkpoints
        self.state_timer = 0
        self.state_change_interval = 180  # Changer d'état toutes les 3 secondes (60 FPS)
        
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
        
        # Variables pour l'exploration autonome
        self.exploration_target_x = x
        self.exploration_target_y = y
        self.exploration_timer = 0
        self.exploration_change_interval = 120  # Changer de cible d'exploration toutes les 2 secondes
        
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
        """Retourner la position actuelle du bot allié"""
        return self.position

    def set_bot_reference(self, bot):
        """Définir la référence au bot principal pour la détection de proximité"""
        self.bot_reference = bot

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

    def update_random_pause_movement(self):
        """Mise à jour des mouvements aléatoires pendant les pauses"""
        self.random_movement_timer += 1
        if self.random_movement_timer >= self.random_movement_interval:
            self.random_movement_timer = 0
            # Générer une nouvelle cible aléatoire proche
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(10, 30)
            self.random_target_x = self.position[0] + math.cos(angle) * distance
            self.random_target_y = self.position[1] + math.sin(angle) * distance

    def update_ai(self):
        """Mise à jour de l'IA du bot allié - système de checkpoints avec pauses"""
        # Vérifier la proximité avec le bot principal
        if self.bot_reference:
            distance_to_bot = self.get_distance_to_bot()
            if distance_to_bot <= self.proximity_distance:
                if not self.is_near_bot:
                    self.is_near_bot = True
                    self.near_bot_timer = 0
                    print(f"AllyBot: Trop proche du bot principal, arrêt et mouvement aléatoire")
            else:
                self.is_near_bot = False

        # Comportement quand proche du bot principal
        if self.is_near_bot:
            self.near_bot_timer += 1
            self.near_bot_movement_timer += 1
            
            # Mouvement aléatoire à côté quand proche du bot
            if self.near_bot_movement_timer >= 20:  # Changer de direction toutes les 0.33 secondes
                self.near_bot_movement_timer = 0
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(15, 40)
                self.target_x = self.position[0] + math.cos(angle) * distance
                self.target_y = self.position[1] + math.sin(angle) * distance
            return  # Ne pas continuer avec le comportement normal

        # Comportement de suivi des checkpoints
        if self.state == "checkpoint_following":
            # Gérer les pauses aux checkpoints
            if self.is_pausing:
                self.pause_timer += 1
                self.update_random_pause_movement()
                self.target_x = self.random_target_x
                self.target_y = self.random_target_y
                
                if self.pause_timer >= self.pause_duration:
                    self.is_pausing = False
                    self.pause_timer = 0
                    print(f"AllyBot: Fin de la pause, reprise du mouvement vers le prochain checkpoint")
                return

            # Vérifier si tous les checkpoints ont été atteints
            if self.current_checkpoint_index >= len(self.checkpoints):
                # Recommencer depuis le premier checkpoint
                self.current_checkpoint_index = 0
                print(f"AllyBot: Tous les checkpoints atteints, recommence depuis le début")
            
            # Obtenir le checkpoint actuel
            current_checkpoint = self.checkpoints[self.current_checkpoint_index]
            distance_to_checkpoint = self.get_distance_to_checkpoint()
            
            # Vérifier si le checkpoint actuel est atteint
            if distance_to_checkpoint <= self.checkpoint_reached_distance:
                print(f"AllyBot: Checkpoint {self.current_checkpoint_index + 1} atteint à {current_checkpoint}")
                print(f"AllyBot: Début de la pause de 4 secondes avec mouvements aléatoires")
                
                # Commencer la pause
                self.is_pausing = True
                self.pause_timer = 0
                self.current_checkpoint_index += 1
                
                # Initialiser le mouvement aléatoire pour la pause
                self.update_random_pause_movement()
                return
            
            # Définir la cible comme le checkpoint actuel
            if self.current_checkpoint_index < len(self.checkpoints):
                self.target_x = current_checkpoint[0]
                self.target_y = current_checkpoint[1]
        
        else:
            # Ancien comportement autonome (gardé pour compatibilité)
            self.state_timer += 1
            if self.state_timer >= self.state_change_interval:
                self.state_timer = 0
                # Changer d'état de manière aléatoire entre exploration et mouvement libre
                states = ["exploring", "wandering"]
                self.state = random.choice(states)
                
                if self.state == "exploring":
                    # Définir une nouvelle cible d'exploration autonome
                    self.set_autonomous_exploration_target()
                elif self.state == "wandering":
                    # Mouvement libre sans cible spécifique
                    self.set_wandering_target()
            
            if self.state == "exploring":
                # Comportement d'exploration autonome
                self.exploration_timer += 1
                if self.exploration_timer >= self.exploration_change_interval:
                    self.exploration_timer = 0
                    self.set_autonomous_exploration_target()
                    
            elif self.state == "wandering":
                # Comportement de déambulation libre
                # Changer de direction de temps en temps
                if random.randint(0, 100) < 2:  # 2% de chance par frame
                    self.set_wandering_target()

    def set_autonomous_exploration_target(self):
        """Définir une nouvelle cible d'exploration autonome"""
        # Exploration dans un rayon autour de la position actuelle
        exploration_radius = 150
        angle = random.uniform(0, 2 * math.pi)
        self.exploration_target_x = self.position[0] + math.cos(angle) * exploration_radius
        self.exploration_target_y = self.position[1] + math.sin(angle) * exploration_radius
        self.target_x = self.exploration_target_x
        self.target_y = self.exploration_target_y

    def set_wandering_target(self):
        """Définir une cible pour le mouvement de déambulation"""
        # Mouvement aléatoire dans un rayon proche
        wander_radius = 80
        angle = random.uniform(0, 2 * math.pi)
        self.target_x = self.position[0] + math.cos(angle) * wander_radius
        self.target_y = self.position[1] + math.sin(angle) * wander_radius

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