import sys

import pygame

from interface.color import WHITE, GRAY
from menu.music import Music


class Menu:



    def __init__(self, screen):
        """Boucle du menu principal"""
        self.SCREEN_WIDTH = screen.get_width()
        self.SCREEN_HEIGHT = screen.get_height()
        self.font = pygame.font.SysFont("arial", 40)
        self.screen = screen
        # Police personnalisée pour les boutons
        try:
            self.button_font = pygame.font.Font("assets/fonts/londrina.ttf", 40)
            self.credits_font = pygame.font.Font("assets/fonts/londrina.ttf", 24)
        except:
            self.button_font = self.font  # Fallback à la police par défaut
            self.credits_font = self.font
        self.play_button = pygame.Rect(self.SCREEN_WIDTH // 2 - 100, self.SCREEN_HEIGHT // 2 - 60, 200, 60)
        self.quit_button = pygame.Rect(self.SCREEN_WIDTH // 2 - 100, self.SCREEN_HEIGHT // 2 + 20, 200, 60)
        self.music = Music(self.screen)
        self.volume_button = self.music.draw_volume_button(self.screen, self.button_font)



    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.play_button.collidepoint(event.pos):
                        self.music.stop_music()
                        return True  # Jouer
                    if self.quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    if self.volume_button.collidepoint(event.pos):
                        self.music.toggle_music()
        return False

    def draw_menu(self):
        """Affiche l'écran du menu principal"""
        # Background
        try:
            background_img = pygame.image.load("assets/images/background.png").convert()
            background_img = pygame.transform.scale(background_img, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.screen.blit(background_img, (0, 0))
        except:
            self.screen.fill(GRAY)  # Fallback si l'image n'existe pas

        # Logo au lieu du titre
        try:
            logo_img = pygame.image.load("assets/images/bthtmc_logo.png").convert_alpha()
            # Redimensionner le logo (ajustez la taille selon vos besoins)
            logo_img = pygame.transform.scale(logo_img, (800, 250))
            logo_x = self.SCREEN_WIDTH // 2 - logo_img.get_width() // 2
            logo_y = self.SCREEN_HEIGHT // 4 - logo_img.get_height() // 2
            self.screen.blit(logo_img, (logo_x, logo_y))
        except:
            # Fallback au titre original si le logo n'existe pas
            title = self.font.render("Bro thinks he's the main character", True, WHITE)
            self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, self.SCREEN_HEIGHT // 4))

        # Vérifier si la souris est sur un bouton pour le curseur
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.play_button.collidepoint(mouse_pos) or self.quit_button.collidepoint(mouse_pos) or self.volume_button.collidepoint(mouse_pos)

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
            pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=10)

            # Bouton principal
            pygame.draw.rect(self.screen, color, rect, border_radius=10)

            # Bordure
            border_color = (255, 255, 255, 150) if is_hovered else (200, 200, 200, 100)
            pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=10)

            # Texte centré avec la police Londrina
            text_surface = self.button_font.render(text, True, text_color)
            text_x = rect.x + rect.width // 2 - text_surface.get_width() // 2
            text_y = rect.y + rect.height // 2 - text_surface.get_height() // 2
            self.screen.blit(text_surface, (text_x, text_y))

        # Nouvelles couleurs
        BLUE_BUTTON = (170, 170, 197)  # #AAAAC5
        BLUE_BUTTON_HOVER = (190, 190, 217)  # Version plus claire pour le hover
        PURPLE_BUTTON = (54, 40, 43)  # #36282B
        PURPLE_BUTTON_HOVER = (74, 60, 63)  # Version plus claire pour le hover

        # Bouton Jouer avec les nouvelles couleurs
        draw_styled_button(self.play_button, "Jouer", BLUE_BUTTON, BLUE_BUTTON_HOVER, WHITE)

        # Bouton Quitter avec les nouvelles couleurs
        draw_styled_button(self.quit_button, "Quitter", PURPLE_BUTTON, PURPLE_BUTTON_HOVER, WHITE)
        draw_styled_button(self.volume_button, self.music.get_volume_button_text(), PURPLE_BUTTON, PURPLE_BUTTON_HOVER, WHITE)

        # Texte des créateurs en bas
        credits_text = "Clément GUERIN - Gabriel MINGOTAUD - Richard HO - Ilyas GHANDAOUI - Léo DESSERTENNE"
        credits_surface = self.credits_font.render(credits_text, True, WHITE)
        credits_x = self.SCREEN_WIDTH // 2 - credits_surface.get_width() // 2
        credits_y = self.SCREEN_HEIGHT - 40  # 40 pixels du bas
        self.screen.blit(credits_surface, (credits_x, credits_y))

        pygame.display.flip()

