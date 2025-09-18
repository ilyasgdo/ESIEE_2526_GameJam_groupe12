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
    
    # Afficher les instructions de contrôle
    print("=== Contrôles du jeu ===")
    print("Mode Clavier (par défaut):")
    print("- WASD/Flèches: Mouvement")
    print("- ESPACE: Tirer")
    print("- G: Placer un piège")
    print("- H: Placer une bombe")
    print()
    print("Basculer entre les modes:")
    print("- C: Activer Computer Vision")
    print("- K: Retour au clavier")
    print()
    print("Mode Computer Vision:")
    print("- 1 doigt levé: Avancer")
    print("- 2 doigts levés: Tourner à gauche")
    print("- 3 doigts levés: Tourner à droite")
    print("- 4 doigts levés: Reculer")
    print("- Poing fermé: Tirer")
    print("- Q dans la fenêtre CV: Fermer la caméra")
    print("="*30)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                game_manager.handle_dialogue()
            # Contrôles pour basculer entre les modes
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                # Basculer vers computer vision
                game_manager.player.set_control_mode("computer_vision")
                print("Mode Computer Vision activé")
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_k:
                # Basculer vers clavier
                game_manager.player.set_control_mode("keyboard")
                print("Mode Clavier activé")
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
