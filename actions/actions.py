import time

import pygame


TAB_ACTION = []

def stunt_hero(hero, action):
    hero.speed = 0
    hero.acceleration = 0
    time.sleep(action.stunt)
    hero.speed = 3
    hero.acceleration = 0.75

def check_trap(hero):
    for i in range(len(TAB_ACTION)):
        action = TAB_ACTION[i]
        x = int(action.pos[0])
        y = int(action.pos[1])

        trap_top = [x+15, y+15]
        trap_bottom = [x, y]

        hero_x = int(hero.position[0])
        hero_y = int(hero.position[1])

        if hero_x < trap_top[0] and hero_x < trap_top[1] and hero_x > trap_bottom[0] and hero_y > trap_bottom[1] and action.active:
            action.active = False
            hero.game_manager.percentage += action.damage
            hero.game_manager.group.remove(action)
            #TAB_ACTION.pop(i)


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

    # placer visuellement


