import pygame


class Intro:



    def __init__(self, game_manager, screen, screen_size):
        # Mise à jour du jeu
        game_manager.update()
        # Rendu
        game_manager.render()

        surface = pygame.Surface(screen_size, pygame.SRCALPHA)
        surface.fill((56, 56, 56, 200))
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        while pygame.event.wait().type != pygame.QUIT:
            pass


