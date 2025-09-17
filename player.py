import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('assets/sprites/player/BIRDSPRITESHEET_Blue.png').convert_alpha()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.position = [x, y]
        self.speed = 3
        self.frame_index = 0
        self.animation_speed = 0.2
        self.current_direction = 'down'
        self.last_direction = 'down'  # Pour mémoriser la dernière direction prioritaire

        # Récupérer toutes les frames
        self.animations = {
            'down': self.load_row(0),
            'left': self.load_row(2),
            'right': self.load_row(1),
            'up': self.load_row(3)
        }

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

    def change_animation(self, direction):
        if self.current_direction != direction:
            self.current_direction = direction
            self.frame_index = 0

    def determine_animation_direction(self):
        """Détermine quelle animation jouer en cas de mouvement diagonal"""
        # Priorité : horizontal > vertical (vous pouvez ajuster selon vos préférences)
        if self.movement_directions['left']:
            return 'left'
        elif self.movement_directions['right']:
            return 'right'
        elif self.movement_directions['up']:
            return 'up'
        elif self.movement_directions['down']:
            return 'down'
        return self.last_direction

    def move_right(self): 
        self.position[0] += self.speed
        self.movement_directions['right'] = True
        self.is_moving = True

    def move_left(self): 
        self.position[0] -= self.speed
        self.movement_directions['left'] = True
        self.is_moving = True

    def move_up(self): 
        self.position[1] -= self.speed
        self.movement_directions['up'] = True
        self.is_moving = True

    def move_down(self): 
        self.position[1] += self.speed
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
        self.rect.topleft = self.position

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
        
        # Remet à zéro les flags de mouvement après l'update
        # (ils seront réactivés lors du prochain appel aux méthodes move_*)
        self.reset_movement_flags()