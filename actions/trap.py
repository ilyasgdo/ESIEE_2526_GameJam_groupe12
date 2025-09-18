import pygame


class Trap(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.damage = 0.5
        self.x = x
        self.y = y
        self.active = True
        self.countdown = 10000

        self.sprite_sheet = pygame.image.load('./traps/Bear_Trap.png')
        self.image = self.get_image(0, 0)
        self.rect = pygame.Rect(x, y, 32, 32)



    def get_image(self, x, y):
        """Récupère une frame depuis le sprite sheet"""
        image = pygame.Surface((32, 32), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image