import pygame
import math

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('./assets/sprites/player/FOXSPRITESHEET.png').convert_alpha()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.position = [x, y]
        self.speed = 3
        self.frame_index = 0
        self.animation_speed = 0.2
        self.current_direction = 'down'
        self.old_position = self.position.copy()

        self.last_direction = 'down'  # Pour mémoriser la dernière direction prioritaire
        
        # Référence au bot allié pour la contrainte de distance
        self.ally_bot = None
        self.max_distance_from_ally = 30000
        
        # Système d'attraction automatique
        self.time_outside_range = 0  # Temps passé hors de portée (en millisecondes)
        self.max_time_outside = 3000  # 3 secondes avant attraction automatique
        self.auto_attraction_speed = 2  # Vitesse d'attraction automatique
        self.is_being_attracted = False  # Flag pour l'attraction en cours

        self.audio = None
        self._was_moving = False

        # Récupérer toutes les frames
        self.animations = {
            'down': self.load_row(5),
            'left': self.load_row(7),
            'right': self.load_row(9),
            'up': self.load_row(11)
        }
        self.feet = pygame.Rect(0, 0, self.rect.width/2, 12)

        self.image = self.animations['down'][0]
        self.is_moving = False
        
        # Variables pour gérer les mouvements multiples
        self.movement_directions = {'up': False, 'down': False, 'left': False, 'right': False}

    def get_image(self, x, y):
        image = pygame.Surface((32, 32), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image

    def load_row(self, row):
        """Charge une ligne de 4 frames à partir du sprite sheet"""
        return [self.get_image(col * 32, row * 32) for col in range(4)]

    def save_location(self): self.old_position = self.position.copy()

    def set_audio(self, audio_manager):
        self.audio = audio_manager

    def change_animation(self, direction):
        if self.current_direction != direction:
            self.current_direction = direction
            self.frame_index = 0
    def determine_animation_direction(self):
        """Détermine la direction d'animation selon les touches pressées"""
        pressed_dirs = [dir for dir, active in self.movement_directions.items() if active]

        if not pressed_dirs:
            return self.last_direction  # aucune touche → garde la dernière direction

        # Priorité horizontal > vertical
        if 'left' in pressed_dirs:
            direction = 'left'
        elif 'right' in pressed_dirs:
            direction = 'right'
        elif 'up' in pressed_dirs:
            direction = 'up'
        elif 'down' in pressed_dirs:
            direction = 'down'
        else:
            direction = self.last_direction

        # mettre à jour last_direction seulement si une touche est active
        if pressed_dirs:
            self.last_direction = direction

        return direction


    def set_ally_bot(self, ally_bot):
        """Définit le bot allié pour la contrainte de distance"""
        self.ally_bot = ally_bot
    
    def get_distance_to_ally(self):
        """Calcule la distance au bot allié"""
        if not self.ally_bot:
            return 0
        ally_pos = self.ally_bot.get_position()
        dx = self.position[0] - ally_pos[0]
        dy = self.position[1] - ally_pos[1]
        return math.sqrt(dx*dx + dy*dy)
    
    def can_move_to(self, new_x, new_y):
        """Vérifie si le joueur peut se déplacer à la position donnée"""
        if not self.ally_bot:
            return True
        
        # Si on est en cours d'attraction automatique, on ne peut pas bouger manuellement
        if self.is_being_attracted:
            return False
        
        ally_pos = self.ally_bot.get_position()
        current_distance = self.get_distance_to_ally()
        
        # Calculer la nouvelle distance après le mouvement
        dx = new_x - ally_pos[0]
        dy = new_y - ally_pos[1]
        new_distance = math.sqrt(dx*dx + dy*dy)
        
        # Si on est dans la limite, on peut bouger
        if new_distance <= self.max_distance_from_ally:
            return True
        
        # Si on est hors limite, on peut seulement bouger si ça nous rapproche
        return new_distance < current_distance

    def move_right(self): 
        new_x = self.position[0] + self.speed
        if self.can_move_to(new_x, self.position[1]):
            self.position[0] = new_x
            self.movement_directions['right'] = True
            self.change_animation('right')
            self.is_moving = True

    def move_left(self): 
        new_x = self.position[0] - self.speed
        if self.can_move_to(new_x, self.position[1]):
            self.position[0] = new_x
            self.movement_directions['left'] = True
            self.change_animation('left')
            self.is_moving = True

    def move_up(self): 
        new_y = self.position[1] - self.speed
        if self.can_move_to(self.position[0], new_y):
            self.position[1] = new_y
            self.movement_directions['up'] = True
            self.change_animation('up')
            self.is_moving = True

    def move_down(self): 
        new_y = self.position[1] + self.speed
        if self.can_move_to(self.position[0], new_y):
            self.position[1] = new_y
            self.movement_directions['down'] = True
            self.change_animation('down')
            self.is_moving = True

    def reset_movement_flags(self):
        """Remet à zéro les flags de mouvement"""
        for direction in self.movement_directions:
            self.movement_directions[direction] = False
        
    def stop(self):
        """Appelé quand aucune touche n'est pressée"""
        self.is_moving = False
        self.reset_movement_flags()
        self.frame_index = 0
        self.image = self.animations[self.current_direction][0]

    def update(self):
        self.rect.center = self.position
        self.feet.move(self.rect.midbottom)

        # Gestion du système d'attraction automatique
        self.update_attraction_system()

        if self.is_moving:
            # Détermine la direction d'animation appropriée
            animation_direction = self.determine_animation_direction()
            # Change l'animation seulement si nécessaire
            if self.current_direction != animation_direction:
                self.change_animation(animation_direction)
            
            self.last_direction = animation_direction
            
            # Met à jour l'animation
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.current_direction]):
                self.frame_index = 0
            self.image = self.animations[self.current_direction][int(self.frame_index)]
        else:
            self.image = self.animations[self.current_direction][0]

        moving_now = self.is_moving
        if self.audio:
            if moving_now and not self._was_moving:
                # Démarre le son quand on commence à bouger
                self.audio.start_running_sound('assets/musics/running_sound.ogg', volume=0.5)
            elif not moving_now and self._was_moving:
                # Coupe le son quand on s'arrête
                self.audio.stop_running_sound(fade_out=80)
        self._was_moving = moving_now

    def move_player_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.move(self.rect.midbottom)

    def move_back(self):
       
        # Remet à zéro les flags de mouvement après l'update
        # (ils seront réactivés lors du prochain appel aux méthodes move_*)
        self.reset_movement_flags()
    
    def update_attraction_system(self):
        """Met à jour le système d'attraction automatique"""
        if not self.ally_bot:
            return
        
        current_distance = self.get_distance_to_ally()
        
        # Si on est hors de portée
        if current_distance > self.max_distance_from_ally:
            # Incrémenter le timer (approximation: 16ms par frame à 60 FPS)
            self.time_outside_range += 16
            
            # Si on a dépassé le temps limite, commencer l'attraction
            if self.time_outside_range >= self.max_time_outside:
                self.is_being_attracted = True
                self.attract_to_ally()
        else:
            # Remettre à zéro le timer si on est dans la portée
            self.time_outside_range = 0
            self.is_being_attracted = False
    
    def attract_to_ally(self):
        """Attire automatiquement le joueur vers le bot allié"""
        if not self.ally_bot:
            return
        
        ally_pos = self.ally_bot.get_position()
        dx = ally_pos[0] - self.position[0]
        dy = ally_pos[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normaliser le vecteur de direction
            dx_normalized = dx / distance
            dy_normalized = dy / distance
            
            # Déplacer vers l'allié
            self.position[0] += dx_normalized * self.auto_attraction_speed
            self.position[1] += dy_normalized * self.auto_attraction_speed
            
            # Changer l'animation selon la direction principale
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.change_animation('right')
                else:
                    self.change_animation('left')
            else:
                if dy > 0:
                    self.change_animation('down')
                else:
                    self.change_animation('up')
            
            self.is_moving = True
            
            # Arrêter l'attraction si on est assez proche
            if distance <= self.max_distance_from_ally * 0.8:  # 80% de la distance max
                self.is_being_attracted = False
                self.time_outside_range = 0
