import pygame


TAB_ACTION = []




def place(action):
    TAB_ACTION.append(action)
    x = action.x
    y = action.y

    sprite_sheet = pygame.image.load(action.image).convert_alpha()
    image = pygame.Surface((32, 32), pygame.SRCALPHA)
    image.blit(sprite_sheet, (0, 0), (x, y, 32, 32))
    rect = image.get_rect()
    # Actualiser l'affichage
    pygame.display.flip()

    print(TAB_ACTION)
    # placer visuellement


