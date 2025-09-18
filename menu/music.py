import pygame

from interface.color import WHITE

music_enabled = True
music_initialized = False

class Music:

    def __init__(self, screen):
        """Initialise et lance la musique du menu"""
        global music_initialized
        if not music_initialized:
            try:
                pygame.mixer.music.load("./assets/musics/full-house.ogg")
                pygame.mixer.music.set_volume(0.3)  # Volume à 30%
                pygame.mixer.music.play(-1)  # -1 pour boucle infinie
                music_initialized = True
            except pygame.error:
                print("Impossible de charger la musique du menu")
        self.SCREEN_WIDTH = screen.get_width()
        self.SCREEN_HEIGHT = screen.get_height()

    def toggle_music(self):
        """Active/désactive la musique"""
        global music_enabled
        music_enabled = not music_enabled
        if music_enabled:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    def stop_music(self):
        pygame.mixer.music.stop()  # Arrêter la musique du menu

    def get_music_enabled(self):
        return music_enabled

    def get_volume_button_text(self):
        # Icône de volume (texte simple)
        volume_text = "ON" if music_enabled else "OFF"
        return volume_text

    def draw_volume_button(self, screen, font):
        """Dessine le bouton de volume en bas à droite"""
        button_size = 40
        margin = 20
        button_rect = pygame.Rect(
            self.SCREEN_WIDTH - button_size - margin,
            self.SCREEN_HEIGHT - button_size - margin,
            button_size,
            button_size
        )

        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_pos)

        # Couleur du bouton selon l'état
        if is_hovered:
            button_color = (100, 100, 100)
        else:
            button_color = (70, 70, 70)

        # Dessiner le bouton
        pygame.draw.rect(screen, button_color, button_rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, button_rect, width=2, border_radius=5)





        return button_rect