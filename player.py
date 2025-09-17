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
        self.old_position = self.position.copy()

        # Récupérer toutes les frames
        self.animations = {
            'down': self.load_row(0),
            'left': self.load_row(2),
            'right': self.load_row(1),
            'up': self.load_row(3)
        }
        self.feet = pygame.Rect(0, 0, self.rect.width/2, 12)

        self.image = self.animations['down'][0]
        self.is_moving = False
    def get_image(self, x, y):
        image = pygame.Surface((32, 32), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image

    def load_row(self, row):
        """Charge une ligne de 4 frames à partir du sprite sheet"""
        return [self.get_image(col * 32, row * 32) for col in range(4)]

    def save_location(self): self.old_position = self.position.copy()

    def change_animation(self, direction):
        if self.current_direction != direction:
            self.current_direction = direction
            self.frame_index = 0

    def move_right(self): 
        self.position[0] += self.speed
        self.change_animation('right')
        self.is_moving = True

    def move_left(self): 
        self.position[0] -= self.speed
        self.change_animation('left')
        self.is_moving = True

    def move_up(self): 
        self.position[1] -= self.speed
        self.change_animation('up')
        self.is_moving = True

    def move_down(self): 
        self.position[1] += self.speed
        self.change_animation('down')
        self.is_moving = True
        
    def stop(self):
        """Appelé quand aucune touche n'est pressée"""
        self.is_moving = False
        self.frame_index = 0
        self.image = self.animations[self.current_direction][0]

    def update(self):
        self.rect.topleft = self.position
        self.feet.move(self.rect.midbottom)
        if self.is_moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.current_direction]):
                self.frame_index = 0
            self.image = self.animations[self.current_direction][int(self.frame_index)]
        else:
            self.image = self.animations[self.current_direction][0]

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.move(self.rect.midbottom)
