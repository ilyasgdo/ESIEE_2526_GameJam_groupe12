#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main entry point for "Tu n'es pas le héros"
Jeu 2D pygame avec bots joueur allié, bot hero et allié joueur
"""

import pygame
import sys
from game.game_manager import GameManager
from menu.menu import Menu

# Configuration de base
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

def main():
    """Point d'entrée principal du jeu"""
    # Initialisation de pygame
    pygame.init()
    pygame.mixer.init()  # Initialiser le mixer pour la musique
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bro thinks he's the main character 💀 - GameJam Groupe 12")

    # Menu principal
    menu = Menu(screen)
    menu.draw_menu()
    started_game = menu.run()
    if not started_game:
        return

    # Lancement du jeu
    clock = pygame.time.Clock()
    game_manager = GameManager(screen)

    game_manager.dialogue_manager.start_scene("scene_intro")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                game_manager.handle_dialogue()
            # Exemple de raccourcis pour tes capacités
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    # Logger la position du joueur
                    player_pos = game_manager.player.position
                    print(f"Position du joueur: x={player_pos[0]:.2f}, y={player_pos[1]:.2f}")
                elif event.key == pygame.K_SPACE:
                    # Déléguer la gestion du dialogue au GameManager
                    game_manager.handle_dialogue()
        

        if not game_manager.dialogue_manager.is_active():
            # Gestion des touches en continu
            game_manager.handle_input()
            # Mise à jour du jeu
            game_manager.update()
        # Rendu
        game_manager.render()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
