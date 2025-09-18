import pygame
import math

class MovementZoneRenderer:
    """Classe pour rendre visuellement la zone de déplacement autorisée du joueur autour de l'ally bot"""
    
    def __init__(self):
        self.zone_color = (100, 150, 255, 80)   # Bleu semi-transparent
        self.border_color = (100, 150, 255, 150)  # Bleu plus opaque pour la bordure
        self.warning_color = (255, 100, 100, 120)  # Rouge pour la zone d'avertissement
        self.border_width = 3
        self.warning_threshold = 0.9  # 90% de la distance max pour commencer l'avertissement
        
        # Animation de la bordure
        self.animation_timer = 0
        self.animation_speed = 0.05
        self.pulse_intensity = 0.3
        
        # Surface pour le rendu avec alpha
        self.zone_surface = None
        self.last_screen_size = None

        # Distance max fixée à 300
        self.fixed_max_distance = 300
        
    def create_zone_surface(self, screen_size):
        """Crée une surface avec canal alpha pour le rendu de la zone"""
        if self.zone_surface is None or self.last_screen_size != screen_size:
            self.zone_surface = pygame.Surface(screen_size, pygame.SRCALPHA).convert_alpha()
            self.last_screen_size = screen_size
        # Toujours reset au début de la frame
        self.zone_surface.fill((0, 0, 0, 0))
        return self.zone_surface

    
    def render_movement_zone(self, screen, player, ally_bot, camera_offset=(0, 0)):
        """
        Rend la zone de déplacement autorisée autour de l'ally bot
        """
        if not ally_bot or not player.ally_bot:
            return
        
        # Obtenir les positions
        ally_pos = ally_bot.get_position()
        player_pos = player.position
        max_distance = self.fixed_max_distance  # forcé à 300
        
        # Calculer les positions à l'écran avec le décalage de la caméra
        screen_ally_x = ally_pos[0] - camera_offset[0]
        screen_ally_y = ally_pos[1] - camera_offset[1]
        screen_player_x = player_pos[0] - camera_offset[0]
        screen_player_y = player_pos[1] - camera_offset[1]
        
        # Créer la surface pour le rendu avec alpha
        zone_surface = self.create_zone_surface(screen.get_size())
        
        # Calculer la distance actuelle
        current_distance = player.get_distance_to_ally()
        distance_ratio = current_distance / max_distance if max_distance > 0 else 0
        
        # Mettre à jour l'animation
        self.animation_timer += self.animation_speed
        pulse = math.sin(self.animation_timer) * self.pulse_intensity + 1.0
        
        # Déterminer les couleurs selon la distance
        if distance_ratio > self.warning_threshold:
            # Zone d'avertissement - rouge pulsant
            zone_color = (
                int(self.warning_color[0]),
                int(self.warning_color[1]),
                int(self.warning_color[2]),
                int(self.warning_color[3] * pulse)
            )
            border_color = (
                255,
                int(100 * pulse),
                int(100 * pulse),
                200
            )
        else:
            # Zone normale - bleu
            zone_color = self.zone_color
            border_color = self.border_color
        
        # Dessiner le cercle de la zone (rempli)
        pygame.draw.circle(
            zone_surface,
            zone_color,
            (int(screen_ally_x), int(screen_ally_y)),
            int(max_distance),
            0  # Rempli
        )
        
        # Dessiner la bordure du cercle
        pygame.draw.circle(
            zone_surface,
            border_color,
            (int(screen_ally_x), int(screen_ally_y)),
            int(max_distance),
            self.border_width
        )
        
        # Dessiner une ligne de connexion entre le joueur et l'ally bot
        connection_color = (255, 255, 255, 100)
        if distance_ratio > self.warning_threshold:
            connection_color = (255, 150, 150, 150)
        
        pygame.draw.line(
            zone_surface,
            connection_color,
            (int(screen_player_x), int(screen_player_y)),
            (int(screen_ally_x), int(screen_ally_y)),
            2
        )
        
        # Indicateur central (ally bot)
        center_bg_color = (30, 30, 30, 200)
        center_border_color = (180, 180, 180, 255)
        
        pygame.draw.circle(
            zone_surface,
            center_bg_color,
            (int(screen_ally_x), int(screen_ally_y)),
            10,
            0
        )
        pygame.draw.circle(
            zone_surface,
            center_border_color,
            (int(screen_ally_x), int(screen_ally_y)),
            10,
            2
        )
        
        # Dessiner un indicateur de distance sur le joueur
        player_indicator_color = (100, 255, 100, 200)
        if distance_ratio > self.warning_threshold:
            player_indicator_color = (255, 100, 100, 200)
        elif distance_ratio > 0.7:
            player_indicator_color = (255, 200, 100, 200)
        
        pygame.draw.circle(
            zone_surface,
            player_indicator_color,
            (int(screen_player_x), int(screen_player_y)),
            6,
            0
        )
        pygame.draw.circle(
            zone_surface,
            (0, 0, 0, 255),
            (int(screen_player_x), int(screen_player_y)),
            6,
            2
        )
        
        # Blitter la surface sur l'écran
        screen.blit(zone_surface, (0, 0))
        

    def render_distance_info(self, screen, player, font=None):
        """Affiche les infos de distance en haut à droite"""
        if not player.ally_bot:
            return
        
        if font is None:
            font = pygame.font.Font(None, 24)
        
        current_distance = player.get_distance_to_ally()
        max_distance = self.fixed_max_distance
        distance_ratio = current_distance / max_distance if max_distance > 0 else 0
        
        # Texte de distance
        distance_text = f"Distance: {current_distance:.0f} / {max_distance:.0f}"
        percentage_text = f"({distance_ratio * 100:.1f}%)"
        
        # Couleur selon la distance
        if distance_ratio > 0.9:
            text_color = (255, 100, 100)  # Rouge
        elif distance_ratio > 0.7:
            text_color = (255, 200, 100)  # Orange
        else:
            text_color = (100, 255, 100)  # Vert
        
        # Rendu du texte
        distance_surface = font.render(distance_text, True, text_color)
        percentage_surface = font.render(percentage_text, True, text_color)
        
        # Position en haut à droite
        screen_width = screen.get_width()
        margin = 10
        
        distance_rect = distance_surface.get_rect()
        distance_rect.topright = (screen_width - margin, margin)
        
        percentage_rect = percentage_surface.get_rect()
        percentage_rect.topright = (screen_width - margin, margin + distance_rect.height + 5)
        
        # Fond semi-transparent
        bg_rect = pygame.Rect(
            distance_rect.left - 5,
            distance_rect.top - 5,
            max(distance_rect.width, percentage_rect.width) + 10,
            distance_rect.height + percentage_rect.height + 15
        )
        
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 120))
        screen.blit(bg_surface, bg_rect.topleft)
        
        # Afficher le texte
        screen.blit(distance_surface, distance_rect)
        screen.blit(percentage_surface, percentage_rect)
