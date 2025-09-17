#!/usr/bin/env python3
"""
Main entry point for "Tu n'es pas le héros" game
Jeu 2D pygame avec bots joueur allié, bot hero et allié joueur
"""

import pygame
import sys
from game_manager import GameManager
from intro import Intro

# Configuration de base
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

def main():
    """Point d'entrée principal du jeu"""
    # Initialisation de pygame
    pygame.init()
    
    # Création de la fenêtre
    screen_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    #screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen = pygame.display.set_mode(screen_size)

    pygame.display.set_caption("Bro thinks he's the main character 💀 - GameJam Groupe 12")

    
    # Horloge pour contrôler les FPS
    clock = pygame.time.Clock()
    
    # Initialisation du gestionnaire de jeu
    game_manager = GameManager(screen)

    intro = Intro(game_manager, screen, screen_size)
    intro.start()


    # Boucle principale du jeu
    running = True
    while running:
    # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            #REMPLACER TOUCHE PAR D'AUTRE KEY OU EVENT
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                # Activer la boule de feu Slot 0 avec un cooldown de 5s
                game_manager.ui.activate_hotbar_slot(0, 5)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                # Activer le Bear Trap Slot 1 avec un cooldown de 10s
                game_manager.ui.activate_hotbar_slot(1, 10)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                # Activer le ???? Slot 2 avec un cooldown de 20s
                game_manager.ui.activate_hotbar_slot(2, 20)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_j:
                # Activer la Tsar Bomba II Slot 3 avec un cooldown de 5s
                game_manager.ui.activate_hotbar_slot(3, 45)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                # Déclencher un stun de 3 secondes (barre du haut)
                game_manager.ui.start_stun(2.5)
        
        # Gestion des touches en continu
        game_manager.handle_input()
        
        # Mise à jour du jeu
        game_manager.update()
        
        # Rendu
        game_manager.render()
    
        # Contrôle des FPS
        clock.tick(FPS)

    
    # Nettoyage et fermeture
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
