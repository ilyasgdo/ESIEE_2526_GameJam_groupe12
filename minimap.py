import pygame
import math

class Minimap:
    def __init__(self, screen, tmx_data, x=10, y=10, width=200, height=150):
        """
        Initialise la minimap
        
        Args:
            screen: Surface pygame principale
            tmx_data: Données de la carte TMX
            x, y: Position de la minimap sur l'écran
            width, height: Dimensions de la minimap
        """
        self.screen = screen
        self.tmx_data = tmx_data
        
        # Position et dimensions de la minimap
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Dimensions du monde en pixels
        self.world_width = tmx_data.width * tmx_data.tilewidth
        self.world_height = tmx_data.height * tmx_data.tileheight
        
        # Facteurs d'échelle pour convertir les coordonnées monde vers minimap
        self.scale_x = self.width / self.world_width
        self.scale_y = self.height / self.world_height
        
        # Surface de la minimap
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Couleurs pour l'interface
        self.bg_color = (30, 30, 40, 180)  # Fond semi-transparent
        self.border_color = (100, 100, 120, 255)  # Bordure
        self.player_color = (0, 255, 0, 255)  # Vert pour le joueur
        self.bot_color = (255, 100, 100, 255)  # Rouge/rose pour le bot
        self.map_color = (80, 80, 90, 255)  # Couleur de base de la carte
        
        # Générer une représentation simplifiée de la carte
        self._generate_map_background()
        
    def _generate_map_background(self):
        """Génère un arrière-plan simplifié de la carte basé sur les couches TMX"""
        # Créer une surface pour l'arrière-plan de la carte
        self.map_background = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Remplir avec une couleur de base
        self.map_background.fill(self.map_color)
        
        # Ajouter quelques détails basés sur les couches de la carte
        # Pour une version simplifiée, on peut dessiner des rectangles représentant les zones importantes
        
        # Dessiner une grille subtile pour représenter la structure de la carte
        grid_spacing = max(5, min(self.width // 20, self.height // 15))
        grid_color = (60, 60, 70, 100)
        
        for x in range(0, self.width, grid_spacing):
            pygame.draw.line(self.map_background, grid_color, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid_spacing):
            pygame.draw.line(self.map_background, grid_color, (0, y), (self.width, y), 1)
    
    def world_to_minimap(self, world_x, world_y):
        """
        Convertit les coordonnées du monde vers les coordonnées de la minimap
        
        Args:
            world_x, world_y: Coordonnées dans le monde du jeu
            
        Returns:
            tuple: (minimap_x, minimap_y) coordonnées sur la minimap
        """
        minimap_x = int(world_x * self.scale_x)
        minimap_y = int(world_y * self.scale_y)
        
        # S'assurer que les coordonnées restent dans les limites de la minimap
        minimap_x = max(0, min(self.width - 1, minimap_x))
        minimap_y = max(0, min(self.height - 1, minimap_y))
        
        return minimap_x, minimap_y
    
    def draw_entity(self, surface, world_x, world_y, color, size=3, shape='circle'):
        """
        Dessine une entité (joueur, bot) sur la minimap
        
        Args:
            surface: Surface sur laquelle dessiner
            world_x, world_y: Position de l'entité dans le monde
            color: Couleur de l'entité
            size: Taille du point représentant l'entité
            shape: Forme ('circle', 'square', 'triangle')
        """
        minimap_x, minimap_y = self.world_to_minimap(world_x, world_y)
        
        if shape == 'circle':
            pygame.draw.circle(surface, color, (minimap_x, minimap_y), size)
            # Bordure pour plus de visibilité
            pygame.draw.circle(surface, (255, 255, 255, 200), (minimap_x, minimap_y), size, 1)
            
        elif shape == 'square':
            rect = pygame.Rect(minimap_x - size, minimap_y - size, size * 2, size * 2)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (255, 255, 255, 200), rect, 1)
            
        elif shape == 'triangle':
            points = [
                (minimap_x, minimap_y - size),
                (minimap_x - size, minimap_y + size),
                (minimap_x + size, minimap_y + size)
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 255, 255, 200), points, 1)
    
    def update(self, player, bot):
        """
        Met à jour la minimap avec les positions actuelles des entités
        
        Args:
            player: Instance du joueur
            bot: Instance du bot
        """
        # Effacer la surface de la minimap
        self.surface.fill((0, 0, 0, 0))  # Transparent
        
        # Dessiner l'arrière-plan de la carte
        self.surface.blit(self.map_background, (0, 0))
        
        # Dessiner le fond semi-transparent
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        self.surface.blit(overlay, (0, 0))
        
        # Dessiner les entités
        if bot:
            self.draw_entity(self.surface, bot.position[0], bot.position[1], 
                           self.bot_color, size=4, shape='square')
        
        if player:
            self.draw_entity(self.surface, player.position[0], player.position[1], 
                           self.player_color, size=5, shape='triangle')
    
    def render(self):
        """Rend la minimap sur l'écran principal"""
        # Dessiner la bordure
        border_rect = pygame.Rect(self.x - 2, self.y - 2, self.width + 4, self.height + 4)
        pygame.draw.rect(self.screen, self.border_color, border_rect)
        pygame.draw.rect(self.screen, (0, 0, 0, 100), border_rect, 2)
        
        # Dessiner la minimap
        self.screen.blit(self.surface, (self.x, self.y))
        
        # Ajouter un titre
        if hasattr(pygame, 'font') and pygame.font.get_init():
            try:
                font = pygame.font.Font(None, 20)
                title_text = font.render("Carte", True, (255, 255, 255))
                title_rect = title_text.get_rect()
                title_rect.centerx = self.x + self.width // 2
                title_rect.bottom = self.y - 5
                
                # Fond pour le titre
                title_bg = pygame.Rect(title_rect.x - 5, title_rect.y - 2, 
                                     title_rect.width + 10, title_rect.height + 4)
                pygame.draw.rect(self.screen, (0, 0, 0, 150), title_bg)
                
                self.screen.blit(title_text, title_rect)
            except:
                # Si la police n'est pas disponible, ignorer le titre
                pass
    
    def set_position(self, x, y):
        """Change la position de la minimap sur l'écran"""
        self.x = x
        self.y = y
    
    def set_size(self, width, height):
        """Change la taille de la minimap"""
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Recalculer les facteurs d'échelle
        self.scale_x = self.width / self.world_width
        self.scale_y = self.height / self.world_height
        
        # Régénérer l'arrière-plan
        self._generate_map_background()