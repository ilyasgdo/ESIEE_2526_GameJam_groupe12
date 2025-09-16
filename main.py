#!/usr/bin/env python3
"""
Main entry point for "Tu n'es pas le héros" game
Jeu 2D pygame avec bots joueur allié, bot hero et allié joueur
"""

import pygame
import sys
from game_manager import GameManager

# Configuration de base
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

def main():
    """Point d'entrée principal du jeu"""
    # Initialisation de pygame
    pygame.init()
    
    # Création de la fenêtre
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tu n'es pas le héros - GameJam Groupe 12")
    
    # Horloge pour contrôler les FPS
    clock = pygame.time.Clock()
    
    # Initialisation du gestionnaire de jeu
    game_manager = GameManager(screen)
    
    # Boucle principale du jeu
    running = True
    while running:
    # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        
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
