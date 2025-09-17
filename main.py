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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Déléguer la gestion du dialogue au GameManager
                    game_manager.handle_dialogue()
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
