import pygame


class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.damage = 1
        self.pos = [x, y]
        self.active = True
        self.countdown = 45000

        self.sprite_sheet = pygame.image.load('./traps/00 All_Rocket.png').subsurface(pygame.Rect(0, 48, 32, 15)).copy()
        self.image = self.get_image(0, 0)
        self.rect = pygame.Rect(x, y, 32, 32)
        self.score = 30
        self.stunt = 5



    def get_image(self, x, y):
        """Récupère une frame depuis le sprite sheet"""
        image = pygame.Surface((32, 32), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))

        return image