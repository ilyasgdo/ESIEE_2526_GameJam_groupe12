import pygame
import math
import cv2
import numpy as np
import mediapipe as mp
import threading
import time

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('./assets/sprites/player/Sousfifre.png').convert_alpha()
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
        self.max_distance_from_ally = 300000
        
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
        
        # Initialiser le contrôleur unifié
        self.controller = PlayerController(self)

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
            self.is_moving = True

    def move_left(self): 
        new_x = self.position[0] - self.speed
        if self.can_move_to(new_x, self.position[1]):
            self.position[0] = new_x
            self.movement_directions['left'] = True
            self.is_moving = True

    def move_up(self): 
        new_y = self.position[1] - self.speed
        if self.can_move_to(self.position[0], new_y):
            self.position[1] = new_y
            self.movement_directions['up'] = True
            self.is_moving = True

    def move_down(self): 
        new_y = self.position[1] + self.speed
        if self.can_move_to(self.position[0], new_y):
            self.position[1] = new_y
            self.movement_directions['down'] = True
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

    def handle_input(self, keys):
        """Méthode pour gérer les entrées selon le mode de contrôle actuel"""
        self.controller.update(keys)
    
    def is_shooting(self, keys=None):
        """Détermine si le joueur veut tirer selon le mode de contrôle"""
        return self.controller.is_shooting(keys)
    
    def set_control_mode(self, mode):
        """Change le mode de contrôle (keyboard ou computer_vision)"""
        self.controller.set_control_mode(mode)
    
    def cleanup(self):
        """Nettoie les ressources du contrôleur"""
        self.controller.cleanup()

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


class ComputerVisionController:
    """Contrôleur de computer vision pour détecter les gestes de la main"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # État des gestes détectés
        self.current_gesture = None
        self.is_fist_closed = False
        self.hand_position = None
        self.previous_hand_position = None
        
        # Caméra
        self.cap = None
        self.camera_active = False
        self.camera_thread = None
        
        # Seuils pour la détection de mouvement
        self.movement_threshold = 0.05
        self.gesture_cooldown = 0.3  # Cooldown en secondes
        self.last_gesture_time = 0
        
    def start_camera(self):
        """Démarre la caméra et le thread de détection"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Erreur: Impossible d'ouvrir la caméra")
                return False
            
            self.camera_active = True
            self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
            self.camera_thread.start()
            print("Caméra démarrée pour la détection de gestes")
            return True
        except Exception as e:
            print(f"Erreur lors du démarrage de la caméra: {e}")
            return False
    
    def stop_camera(self):
        """Arrête la caméra"""
        self.camera_active = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("Caméra arrêtée")
    
    def _camera_loop(self):
        """Boucle principale de traitement de la caméra (sans affichage)"""
        while self.camera_active:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Retourner l'image horizontalement pour un effet miroir
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Détecter les mains
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Analyser les gestes (sans dessiner)
                    self._analyze_gesture(hand_landmarks, frame.shape)
            else:
                # Aucune main détectée
                self.current_gesture = None
                self.is_fist_closed = False
                self.hand_position = None
            
            # Pas d'affichage de fenêtre - traitement en arrière-plan uniquement
            # La détection continue sans interface visuelle
    
    def _analyze_gesture(self, hand_landmarks, frame_shape):
        """Analyse les gestes de la main"""
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.append([lm.x, lm.y])
        
        # Position du centre de la main (poignet)
        wrist = landmarks[0]
        self.previous_hand_position = self.hand_position
        self.hand_position = wrist
        
        # Détecter le poing fermé (pour le tir)
        self.is_fist_closed = self._is_fist_closed(landmarks)
        
        # Compter les doigts levés et déterminer le geste
        if time.time() - self.last_gesture_time > self.gesture_cooldown:
            finger_count = self._count_fingers(landmarks)
            gesture = self._map_finger_count_to_gesture(finger_count)
            if gesture:
                self.current_gesture = gesture
                self.last_gesture_time = time.time()
    
    def _is_fist_closed(self, landmarks):
        """Détermine si la main forme un poing fermé"""
        # Points des doigts (tips) et des articulations (pips)
        finger_tips = [4, 8, 12, 16, 20]  # Pouce, index, majeur, annulaire, auriculaire
        finger_pips = [3, 6, 10, 14, 18]  # Articulations correspondantes
        
        closed_fingers = 0
        
        # Vérifier chaque doigt
        for i in range(5):
            tip = landmarks[finger_tips[i]]
            pip = landmarks[finger_pips[i]]
            
            # Pour le pouce, vérifier différemment
            if i == 0:  # Pouce
                if tip[0] > pip[0]:  # Pouce replié vers la droite
                    closed_fingers += 1
            else:  # Autres doigts
                if tip[1] > pip[1]:  # Bout du doigt plus bas que l'articulation
                    closed_fingers += 1
        
        # Poing fermé si au moins 4 doigts sont repliés
        return closed_fingers >= 4
    
    def _count_fingers(self, landmarks):
        """Compte le nombre de doigts levés"""
        # Points des doigts (tips) et des articulations
        finger_tips = [4, 8, 12, 16, 20]  # Pouce, index, majeur, annulaire, auriculaire
        finger_pips = [3, 6, 10, 14, 18]  # Articulations correspondantes
        finger_mcp = [2, 5, 9, 13, 17]   # Articulations de base
        
        fingers_up = 0
        
        # Vérifier chaque doigt
        for i in range(5):
            tip = landmarks[finger_tips[i]]
            pip = landmarks[finger_pips[i]]
            mcp = landmarks[finger_mcp[i]]
            
            # Pour le pouce, vérifier différemment (mouvement horizontal)
            if i == 0:  # Pouce
                if tip[0] < pip[0]:  # Pouce levé vers la gauche
                    fingers_up += 1
            else:  # Autres doigts (mouvement vertical)
                if tip[1] < pip[1] and pip[1] < mcp[1]:  # Bout du doigt plus haut que l'articulation
                    fingers_up += 1
        
        return fingers_up
    
    def _map_finger_count_to_gesture(self, finger_count):
        """Mappe le nombre de doigts levés à un geste"""
        gesture_map = {
            1: 'forward',      # 1 doigt = avancer
            2: 'turn_left',    # 2 doigts = tourner à gauche
            3: 'turn_right',   # 3 doigts = tourner à droite
            4: 'backward',     # 4 doigts = reculer
            5: None            # 5 doigts = pas de mouvement (main ouverte)
        }
        return gesture_map.get(finger_count, None)

    def _detect_movement(self, prev_pos, curr_pos):
        """Détecte les mouvements de direction"""
        if not prev_pos or not curr_pos:
            return None
        
        dx = curr_pos[0] - prev_pos[0]
        dy = curr_pos[1] - prev_pos[1]
        
        # Vérifier si le mouvement est assez significatif
        if abs(dx) < self.movement_threshold and abs(dy) < self.movement_threshold:
            return None
        
        # Déterminer la direction principale
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'
    
    def get_current_gesture(self):
        """Retourne le geste actuel détecté"""
        return self.current_gesture
    
    def is_shooting_gesture(self):
        """Retourne True si le geste de tir (poing fermé) est détecté"""
        return self.is_fist_closed
    
    def reset_gesture(self):
        """Remet à zéro le geste actuel"""
        self.current_gesture = None


class PlayerController:
    """Contrôleur unifié pour gérer les entrées clavier et computer vision"""
    
    def __init__(self, player):
        self.player = player
        self.cv_controller = ComputerVisionController()
        self.control_mode = "keyboard"  # "keyboard" ou "computer_vision"
        self.cv_active = False
        
    def set_control_mode(self, mode):
        """Change le mode de contrôle"""
        if mode == "computer_vision" and not self.cv_active:
            if self.cv_controller.start_camera():
                self.cv_active = True
                self.control_mode = mode
                print("Mode computer vision activé")
            else:
                print("Impossible d'activer le mode computer vision")
        elif mode == "keyboard":
            if self.cv_active:
                self.cv_controller.stop_camera()
                self.cv_active = False
            self.control_mode = mode
            print("Mode clavier activé")
    
    def handle_keyboard_input(self, keys):
        """Gère les entrées clavier traditionnelles"""
        if self.control_mode != "keyboard":
            return
        
        # Réinitialiser les flags de mouvement
        self.player.reset_movement_flags()
        self.player.is_moving = False
        
        # Gérer les mouvements
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move_up()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move_down()
        
        # Si aucune touche n'est pressée, arrêter le mouvement
        if not any([keys[pygame.K_RIGHT], keys[pygame.K_LEFT], 
                   keys[pygame.K_UP], keys[pygame.K_DOWN],
                   keys[pygame.K_d], keys[pygame.K_a], 
                   keys[pygame.K_w], keys[pygame.K_s]]):
            self.player.stop()
    
    def handle_computer_vision_input(self):
        """Gère les entrées de computer vision avec vitesse augmentée"""
        if self.control_mode != "computer_vision" or not self.cv_active:
            return
        
        # Sauvegarder la vitesse originale et augmenter temporairement
        original_speed = self.player.speed
        self.player.speed = 40# Doubler la vitesse en mode CV (3 -> 6)
        
        # Réinitialiser les flags de mouvement
        self.player.reset_movement_flags()
        self.player.is_moving = False
        
        # Obtenir le geste actuel
        gesture = self.cv_controller.get_current_gesture()
        
        if gesture:
            if gesture == 'forward':
                self.player.move_up()  # Avancer = vers le haut
            elif gesture == 'backward':
                self.player.move_down()  # Reculer = vers le bas
            elif gesture == 'turn_left':
                self.player.move_left()  # Tourner à gauche = aller à gauche
            elif gesture == 'turn_right':
                self.player.move_right()  # Tourner à droite = aller à droite
            
            # Réinitialiser le geste après traitement
            self.cv_controller.reset_gesture()
        else:
            self.player.stop()
        
        # Restaurer la vitesse originale
        self.player.speed = original_speed
    
    def is_shooting(self, keys=None):
        """Détermine si le joueur veut tirer"""
        if self.control_mode == "keyboard" and keys:
            return keys[pygame.K_SPACE]
        elif self.control_mode == "computer_vision":
            return self.cv_controller.is_shooting_gesture()
        return False
    
    def update(self, keys=None):
        """Met à jour le contrôleur selon le mode actuel"""
        if self.control_mode == "keyboard":
            if keys:
                self.handle_keyboard_input(keys)
        elif self.control_mode == "computer_vision":
            self.handle_computer_vision_input()
    
    def cleanup(self):
        """Nettoie les ressources"""
        if self.cv_active:
            self.cv_controller.stop_camera()
