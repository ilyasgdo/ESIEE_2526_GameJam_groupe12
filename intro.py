import time

import pygame


class Intro:

    TEXT = ["Introduction", "Vous êtes les méchants", "Le héro arrive"]

    def __init__(self, game_manager, screen, screen_size):
        self.screen = screen
        self.screen_size = screen_size
        self.screen_width = screen_size[0]
        self.screen_height = screen_size[1]
        self.game_manager = game_manager


    def start(self):
        font = pygame.font.Font(None, 24)
        for libelle in Intro.TEXT:
            # Mise à jour du jeu
            self.game_manager.update()
            # Rendu
            self.game_manager.render()
            surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            surface.fill((56, 56, 56, 200))
            self.screen.blit(surface, (0, 0))
            text = font.render(libelle, 1, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen_width/ 2, self.screen_height/2))
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            time.sleep(3)




