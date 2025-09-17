#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main entry point for "Tu n'es pas le héros"
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

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
BLUE = (0, 120, 255)
RED = (200, 50, 50)


def draw_menu(screen, font, play_button, quit_button):
    """Affiche l’écran du menu principal"""
    screen.fill(GRAY)
    title = font.render("Bro thinks he's the main character", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 4))
    skull_img = pygame.image.load("assets/images/skull.png").convert_alpha()
    skull_img = pygame.transform.scale(skull_img, (64, 64))  

    # Dans draw_menu()
    screen.blit(skull_img, (SCREEN_WIDTH//2 - 32, SCREEN_HEIGHT//4 - 80))
    # Bouton Jouer
    pygame.draw.rect(screen, BLUE, play_button)
    play_text = font.render("Jouer", True, WHITE)
    screen.blit(play_text, (play_button.x + play_button.width // 2 - play_text.get_width() // 2,
                            play_button.y + 10))

    # Bouton Quitter
    pygame.draw.rect(screen, RED, quit_button)
    quit_text = font.render("Quitter", True, WHITE)
    screen.blit(quit_text, (quit_button.x + quit_button.width // 2 - quit_text.get_width() // 2,
                            quit_button.y + 10))

    pygame.display.flip()


def main_menu(screen):
    """Boucle du menu principal"""
    font = pygame.font.SysFont("arial", 40)
    play_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60, 200, 60)
    quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 60)

    running = True
    while running:
        draw_menu(screen, font, play_button, quit_button)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button.collidepoint(event.pos):
                    return True   # Jouer
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
    return False


def main():
    """Point d'entrée principal du jeu"""
    # Initialisation de pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bro thinks he's the main character 💀 - GameJam Groupe 12")

    # Menu principal
    start_game = main_menu(screen)
    if not start_game:
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
                if event.key == pygame.K_f:
                    game_manager.ui.activate_hotbar_slot(0, 5)
                elif event.key == pygame.K_g:
                    game_manager.ui.activate_hotbar_slot(1, 10)
                elif event.key == pygame.K_h:
                    game_manager.ui.activate_hotbar_slot(2, 20)
                elif event.key == pygame.K_j:
                    game_manager.ui.activate_hotbar_slot(3, 45)
                elif event.key == pygame.K_o:
                    game_manager.ui.start_stun(2.5)
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
