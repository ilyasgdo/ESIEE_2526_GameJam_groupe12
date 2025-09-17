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
    """Affiche l'écran du menu principal"""
    # Background
    try:
        background_img = pygame.image.load("assets/images/background.png").convert()
        background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(background_img, (0, 0))
    except:
        screen.fill(GRAY)  # Fallback si l'image n'existe pas

    # Logo au lieu du titre
    try:
        logo_img = pygame.image.load("assets/images/bthtmc_logo.png").convert_alpha()
        # Redimensionner le logo (ajustez la taille selon vos besoins)
        logo_img = pygame.transform.scale(logo_img, (800, 250))
        logo_x = SCREEN_WIDTH // 2 - logo_img.get_width() // 2
        logo_y = SCREEN_HEIGHT // 4 - logo_img.get_height() // 2
        screen.blit(logo_img, (logo_x, logo_y))
    except:
        # Fallback au titre original si le logo n'existe pas
        title = font.render("Bro thinks he's the main character", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 4))

    # Police personnalisée pour les boutons
    try:
        button_font = pygame.font.Font("assets/fonts/londrina.ttf", 40)
        credits_font = pygame.font.Font("assets/fonts/londrina.ttf", 24)
    except:
        button_font = font  # Fallback à la police par défaut
        credits_font = font

    # Vérifier si la souris est sur un bouton pour le curseur
    mouse_pos = pygame.mouse.get_pos()
    is_hovering = play_button.collidepoint(mouse_pos) or quit_button.collidepoint(mouse_pos)

    if is_hovering:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    # Style amélioré pour les boutons
    def draw_styled_button(rect, text, base_color, hover_color, text_color):
        is_hovered = rect.collidepoint(mouse_pos)
        color = hover_color if is_hovered else base_color

        # Ombre du bouton
        shadow_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width, rect.height)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)

        # Bouton principal
        pygame.draw.rect(screen, color, rect, border_radius=10)

        # Bordure
        border_color = (255, 255, 255, 150) if is_hovered else (200, 200, 200, 100)
        pygame.draw.rect(screen, border_color, rect, width=2, border_radius=10)

        # Texte centré avec la police Londrina
        text_surface = button_font.render(text, True, text_color)
        text_x = rect.x + rect.width // 2 - text_surface.get_width() // 2
        text_y = rect.y + rect.height // 2 - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))

    # Nouvelles couleurs
    BLUE_BUTTON = (170, 170, 197)  # #AAAAC5
    BLUE_BUTTON_HOVER = (190, 190, 217)  # Version plus claire pour le hover
    PURPLE_BUTTON = (54, 40, 43)  # #36282B
    PURPLE_BUTTON_HOVER = (74, 60, 63)  # Version plus claire pour le hover

    # Bouton Jouer avec les nouvelles couleurs
    draw_styled_button(play_button, "Jouer", BLUE_BUTTON, BLUE_BUTTON_HOVER, WHITE)

    # Bouton Quitter avec les nouvelles couleurs
    draw_styled_button(quit_button, "Quitter", PURPLE_BUTTON, PURPLE_BUTTON_HOVER, WHITE)

    # Texte des créateurs en bas
    credits_text = "Clément GUERIN - Gabriel MINGOTAUD - Richard HO - Ilyas GHANDAOUI - Léo DESSERTENNE"
    credits_surface = credits_font.render(credits_text, True, WHITE)
    credits_x = SCREEN_WIDTH // 2 - credits_surface.get_width() // 2
    credits_y = SCREEN_HEIGHT - 40  # 40 pixels du bas
    screen.blit(credits_surface, (credits_x, credits_y))

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
                elif event.key == pygame.K_SPACE:
                    # Déléguer la gestion du dialogue au GameManager
                    game_manager.handle_dialogue()
                elif event.key == pygame.K_l:
                    # Logger la position du joueur
                    player_pos = game_manager.player.position
                    print(f"Position du joueur: x={player_pos[0]:.2f}, y={player_pos[1]:.2f}")
        
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
