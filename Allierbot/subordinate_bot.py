import pygame
import math
import random
from actions.fire_ball import FireBall
from actions.bomb import Bomb
from actions.trap import Trap
from actions.actions import TAB_ACTION

class SubordinateBot(pygame.sprite.Sprite):
    def __init__(self, x, y, leader, formation_angle, formation_radius=60):
        super().__init__()
        # Utiliser le même sprite sheet que le joueur mais avec une couleur différente
        self.sprite_sheet = pygame.image.load('./assets/sprites/player/Sousfifre.png').convert_alpha()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.position = [float(x), float(y)]
        self.old_position = self.position.copy()  # Pour la gestion des collisions
        self.speed = 15  # Légèrement plus rapide pour rattraper le leader
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
        self.max_speed = 15.0
        
        # Variables pour des mouvements plus naturels
        self.micro_movement_timer = 0
        self.micro_movement_x = 0
        self.micro_movement_y = 0
        self.breathing_timer = random.uniform(0, math.pi * 2)
        self.hesitation_timer = 0
        self.is_hesitating = False
        self.natural_speed_variation = 1.0
        self.last_direction_change = 0
        
        # Variables pour mouvement aléatoire autour de l'ally bot
        self.random_angle_offset = random.uniform(-math.pi/3, math.pi/3)  # Offset aléatoire de l'angle
        self.random_radius_offset = random.uniform(-20, 20)  # Variation du rayon
        self.angle_drift_speed = random.uniform(0.005, 0.02)  # Vitesse de dérive de l'angle
        self.radius_oscillation_timer = random.uniform(0, math.pi * 2)
        self.radius_oscillation_speed = random.uniform(0.01, 0.03)
        self.position_change_timer = random.randint(60, 180)  # Timer pour changer de position
        self.target_angle_offset = self.random_angle_offset
        
        # Variables pour suivi de trajectoire de l'ally bot
        self.leader_previous_position = list(leader.get_position()) if leader else [0, 0]
        self.leader_velocity = [0, 0]
        self.trajectory_prediction_factor = 0.3  # Facteur de prédiction de trajectoire
        self.velocity_smoothing = 0.1  # Lissage de la vélocité du leader
        
        # Variables pour cohérence directionnelle avec l'ally bot
        self.leader_direction_influence = 0.4  # Influence de la direction du leader
        self.direction_alignment_speed = 0.05  # Vitesse d'alignement directionnel
        self.preferred_direction_offset = random.uniform(-math.pi/4, math.pi/4)  # Offset préféré par rapport au leader
        
        # Variables pour éviter les collisions entre subordonnés
        self.separation_radius = 25
        self.cohesion_strength = 0.1
        self.separation_strength = 0.5
        
        # Variables pour l'évitement de collision
        self.separation_force = [0, 0]
        self.cohesion_force = [0, 0]
        
        # Système de collision avec les objets TMX
        self.collision_objects = []
        
        # Variables pour le système de tir et piège aléatoire
        self.last_action_time = pygame.time.get_ticks()
        self.action_interval = 10000  # 10 secondes en millisecondes
        self.action_probability = 0.1  # 50% de probabilité d'effectuer une action
        
        # Récupérer toutes les frames (même système que le joueur)
        self.animations = {
            'down': self.load_row(5),
            'left': self.load_row(7),
            'right': self.load_row(9),
            'up': self.load_row(11)
        }
        
        # Appliquer une teinte bleue pour distinguer les subordonnés
        self.apply_tint((150, 200, 255))  # Teinte bleue
        
        self.image = self.animations['up'][0]
        self.is_moving = True

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
        """Calcule la position cible dans la formation autour du leader avec mouvement aléatoire et suivi de trajectoire"""
        if not self.leader:
            return self.position
        
        leader_pos = self.leader.get_position()
        
        # Calculer la vélocité du leader pour prédire sa trajectoire
        current_leader_velocity = [
            leader_pos[0] - self.leader_previous_position[0],
            leader_pos[1] - self.leader_previous_position[1]
        ]
        
        # Lisser la vélocité du leader pour éviter les changements brusques
        self.leader_velocity[0] += (current_leader_velocity[0] - self.leader_velocity[0]) * self.velocity_smoothing
        self.leader_velocity[1] += (current_leader_velocity[1] - self.leader_velocity[1]) * self.velocity_smoothing
        
        # Prédire la position future du leader basée sur sa trajectoire
        predicted_leader_x = leader_pos[0] + self.leader_velocity[0] * self.trajectory_prediction_factor * 10
        predicted_leader_y = leader_pos[1] + self.leader_velocity[1] * self.trajectory_prediction_factor * 10
        
        # Mettre à jour la position précédente du leader
        self.leader_previous_position = list(leader_pos)
        
        # Mettre à jour le timer pour changer de position aléatoirement
        self.position_change_timer -= 1
        if self.position_change_timer <= 0:
            # Changer vers une nouvelle position aléatoire
            self.target_angle_offset = random.uniform(-math.pi/2, math.pi/2)
            self.random_radius_offset = random.uniform(-25, 25)
            self.position_change_timer = random.randint(120, 300)  # 2-5 secondes à 60 FPS
        
        # Transition douce vers le nouvel angle cible
        angle_diff = self.target_angle_offset - self.random_angle_offset
        if abs(angle_diff) > math.pi:
            if angle_diff > 0:
                angle_diff -= 2 * math.pi
            else:
                angle_diff += 2 * math.pi
        
        self.random_angle_offset += angle_diff * 0.02  # Transition douce
        
        # Dérive continue de l'angle pour un mouvement plus naturel
        self.random_angle_offset += self.angle_drift_speed * random.uniform(-1, 1)
        
        # Oscillation du rayon pour un mouvement plus dynamique
        self.radius_oscillation_timer += self.radius_oscillation_speed
        radius_oscillation = math.sin(self.radius_oscillation_timer) * 8
        
        # Calculer l'angle final avec l'offset aléatoire
        final_angle = self.formation_angle + self.random_angle_offset
        final_radius = self.formation_radius + self.random_radius_offset + radius_oscillation
        
        # Calculer la position cible avec le mouvement aléatoire et le suivi de trajectoire
        # Utiliser la position prédite du leader au lieu de sa position actuelle
        target_x = predicted_leader_x + math.cos(final_angle) * final_radius
        target_y = predicted_leader_y + math.sin(final_angle) * final_radius
        
        return [target_x, target_y]

    def update_formation_movement(self, subordinates_list):
        """Met à jour le mouvement pour maintenir la formation avec des comportements plus naturels"""
        if not self.leader:
            return
        
        # Calculer la position cible dans la formation
        self.target_position = self.calculate_formation_position()
        
        # Micro-mouvements pour simuler l'imprécision naturelle
        self.micro_movement_timer += 1
        if self.micro_movement_timer >= random.randint(3, 8):  # Variation dans le timing
            self.micro_movement_timer = 0
            self.micro_movement_x = random.uniform(-0.15, 0.15)
            self.micro_movement_y = random.uniform(-0.15, 0.15)
        
        # Effet de "respiration" subtil
        self.breathing_timer += 0.08 + random.uniform(-0.02, 0.02)  # Variation du rythme
        breathing_effect_x = math.sin(self.breathing_timer) * 0.08
        breathing_effect_y = math.cos(self.breathing_timer * 0.7) * 0.06
        
        # Ajouter les effets naturels à la position cible
        adjusted_target_x = self.target_position[0] + self.micro_movement_x + breathing_effect_x
        adjusted_target_y = self.target_position[1] + self.micro_movement_y + breathing_effect_y
        
        # Calculer la direction vers la position cible
        dx = adjusted_target_x - self.position[0]
        dy = adjusted_target_y - self.position[1]
        distance_to_target = math.sqrt(dx*dx + dy*dy)
        
        # Cohérence directionnelle avec l'ally bot
        leader_direction = 0
        if abs(self.leader_velocity[0]) > 0.1 or abs(self.leader_velocity[1]) > 0.1:
            # Calculer la direction du leader basée sur sa vélocité
            leader_direction = math.atan2(self.leader_velocity[1], self.leader_velocity[0])
            
            # Ajuster la direction cible pour être cohérente avec le leader
            target_direction = math.atan2(dy, dx)
            
            # Calculer la direction préférée (direction du leader + offset personnel)
            preferred_direction = leader_direction + self.preferred_direction_offset
            
            # Mélanger la direction vers la cible avec la direction préférée
            direction_diff = preferred_direction - target_direction
            if abs(direction_diff) > math.pi:
                if direction_diff > 0:
                    direction_diff -= 2 * math.pi
                else:
                    direction_diff += 2 * math.pi
            
            # Appliquer l'influence directionnelle du leader
            adjusted_direction = target_direction + direction_diff * self.leader_direction_influence
            
            # Recalculer dx et dy avec la direction ajustée
            if distance_to_target > 0:
                dx = math.cos(adjusted_direction) * distance_to_target
                dy = math.sin(adjusted_direction) * distance_to_target
        
        # Hésitation occasionnelle quand on change de direction significativement
        if distance_to_target > 5:
            current_direction = math.atan2(dy, dx)
            if abs(current_direction - self.last_direction_change) > 0.5:  # Changement significatif
                if random.random() < 0.2 and not self.is_hesitating:  # 20% de chance
                    self.is_hesitating = True
                    self.hesitation_timer = random.randint(8, 20)
                    self.last_direction_change = current_direction
        
        # Gérer l'hésitation
        if self.is_hesitating:
            self.hesitation_timer -= 1
            if self.hesitation_timer <= 0:
                self.is_hesitating = False
            # Réduire le mouvement pendant l'hésitation
            self.natural_speed_variation = 0.2 + random.uniform(0, 0.3)
        else:
            # Variation naturelle de la vitesse basée sur la distance
            base_variation = 0.7 + random.uniform(0, 0.5)
            # Plus on est loin, plus on va vite (dans une certaine mesure)
            distance_factor = min(1.2, 0.8 + distance_to_target * 0.01)
            self.natural_speed_variation = base_variation * distance_factor
        
        # Force d'attraction vers la position de formation
        if distance_to_target > 2:  # Zone morte pour éviter les oscillations
            force_x = (dx / distance_to_target) * self.acceleration
            force_y = (dy / distance_to_target) * self.acceleration
        else:
            force_x = force_y = 0
        
        # Force de séparation avec les autres subordonnés
        separation_x, separation_y = self.calculate_separation(subordinates_list)
        
        # Ajouter une variation naturelle à la force de séparation
        separation_x *= (0.8 + random.uniform(0, 0.4))
        separation_y *= (0.8 + random.uniform(0, 0.4))
        
        # Transition plus douce vers la nouvelle vélocité
        transition_speed = 0.12 if not self.is_hesitating else 0.04
        target_velocity_x = force_x + separation_x * self.separation_strength
        target_velocity_y = force_y + separation_y * self.separation_strength
        
        self.velocity_x += (target_velocity_x - self.velocity_x) * transition_speed
        self.velocity_y += (target_velocity_y - self.velocity_y) * transition_speed
        
        # Appliquer la variation de vitesse naturelle
        adjusted_velocity_x = self.velocity_x * self.natural_speed_variation
        adjusted_velocity_y = self.velocity_y * self.natural_speed_variation
        
        # Appliquer une friction variable
        friction = self.friction + random.uniform(-0.03, 0.03)
        adjusted_velocity_x *= friction
        adjusted_velocity_y *= friction
        
        # Limiter la vitesse maximale avec une variation naturelle
        current_max_speed = self.max_speed * (0.8 + random.uniform(0, 0.4))
        speed = math.sqrt(adjusted_velocity_x**2 + adjusted_velocity_y**2)
        if speed > current_max_speed:
            adjusted_velocity_x = (adjusted_velocity_x / speed) * current_max_speed
            adjusted_velocity_y = (adjusted_velocity_y / speed) * current_max_speed
        
        # Sauvegarder la position actuelle avant le mouvement
        self.save_position()
        
        # Calculer la nouvelle position
        new_x = self.position[0] + adjusted_velocity_x
        new_y = self.position[1] + adjusted_velocity_y
        
        # Vérifier les collisions avant de se déplacer
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

        # Déterminer la direction d'animation avec plus de fluidité
        if abs(adjusted_velocity_x) > abs(adjusted_velocity_y):
            if adjusted_velocity_x > 0.15:
                self.change_animation('right')
            elif adjusted_velocity_x < -0.15:
                self.change_animation('left')
        else:
            if adjusted_velocity_y > 0.15:
                self.change_animation('down')
            elif adjusted_velocity_y < -0.15:
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

    def handle_random_action(self, fireballs_group, group):
        """Gère les actions aléatoires (tir, bombe ou piège) toutes les 10 secondes avec 50% de probabilité"""
        current_time = pygame.time.get_ticks()
        
        # Vérifier si 10 secondes se sont écoulées
        if current_time - self.last_action_time >= self.action_interval:
            # 50% de probabilité d'effectuer une action
            if random.random() < self.action_probability:
                # Choisir aléatoirement entre tir (0), bombe (1) et piège (2)
                action_choice = random.randint(0, 2)
                
                if action_choice == 0:
                    # Tirer une boule de feu
                    self.shoot_fireball(fireballs_group, group)
                elif action_choice == 1:
                    # Lancer une bombe
                    self.launch_bomb(group)
                else:
                    # Poser un piège
                    self.place_trap(group)
            
            # Réinitialiser le timer
            self.last_action_time = current_time

    def shoot_fireball(self, fireballs_group, group):
        """Tire une boule de feu dans la direction actuelle"""
        fireball = FireBall(
            self.position[0] + 16,  # Centre du sprite
            self.position[1] + 16,
            self.current_direction
        )
        fireballs_group.add(fireball)
        group.add(fireball)

    def launch_bomb(self, group):
        """Lance une bombe à la position actuelle"""
        bomb = Bomb(
            self.position[0] + 16,  # Centre du sprite
            self.position[1] + 16   # Centre du sprite
        )
        TAB_ACTION.append(bomb)
        group.add(bomb)

    def place_trap(self, group):
        """Place un piège à la position actuelle"""
        trap = Trap(self.position[0], self.position[1])
        TAB_ACTION.append(trap)
        group.add(trap)

    def update(self, subordinates_list=None, fireballs_group=None, group=None):
        """Met à jour le subordonné"""
        # Mettre à jour le mouvement de formation
        if subordinates_list is None:
            subordinates_list = []
        self.update_formation_movement(subordinates_list)
        
        # Gérer les actions aléatoires si les groupes sont fournis
        if fireballs_group is not None and group is not None:
            self.handle_random_action(fireballs_group, group)
        
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