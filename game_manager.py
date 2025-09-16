#!/usr/bin/env python3
"""
Game Manager pour "Tu n'es pas le héros"
Version simplifiée - chargement de map uniquement avec diagnostics
"""

import pygame
import sys
import os
import pytmx
import pyscroll

from player import Player

class GameManager:
    """Gestionnaire principal du jeu"""
    
    def __init__(self, screen):
        """Initialisation du gestionnaire de jeu"""
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # Variables pour le chargement de map
        self.map_loaded = False
        self.group = None
        self.tmx_data = None
        self.error_message = None
        
        # Variables pour la caméra
        self.camera_x = 0
        self.camera_y = 0
        self.map_width = 0
        self.map_height = 0
        
        # Initialisation du niveau
        self._init_level()
        
        # Création du joueur
        self.player = Player(100, 100)
        if self.group:
            self.group.add(self.player)
        
        # Police pour l'interface
        self.font = pygame.font.Font(None, 24)
    
    def _create_fallback_tileset(self, tileset):
        """Crée une image de fallback pour un tileset manquant"""
        try:
            # Créer une surface de fallback
            tile_size = tileset.tilewidth
            columns = tileset.columns
            rows = (tileset.tilecount + columns - 1) // columns
            
            fallback_surface = pygame.Surface((columns * tile_size, rows * tile_size))
            
            # Couleurs différentes pour chaque tileset
            colors = {
                'TX Props': (255, 100, 100),      # Rouge
                'grass': (100, 255, 100),         # Vert
                'TX Tileset Wall': (150, 150, 150), # Gris
                'escalier': (255, 200, 100),      # Orange
                'props': (200, 100, 255)          # Violet
            }
            
            base_color = colors.get(tileset.name, (128, 128, 128))
            
            # Remplir avec un motif
            for y in range(rows):
                for x in range(columns):
                    if y * columns + x < tileset.tilecount:
                        # Créer une tuile avec un motif
                        tile_rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                        
                        # Couleur de base avec variation
                        color = tuple(max(0, min(255, c + (x + y) * 10)) for c in base_color)
                        fallback_surface.fill(color, tile_rect)
                        
                        # Ajouter un contour
                        pygame.draw.rect(fallback_surface, (0, 0, 0), tile_rect, 1)
            
            # Remplacer l'image du tileset
            tileset.image = fallback_surface
            print(f"    Image de fallback créée pour {tileset.name}")
            
        except Exception as e:
            print(f"    Erreur lors de la création du fallback: {e}")
    
    def _create_fallback_renderer(self):
        """Crée un système de rendu de fallback sans pyscroll"""
        print("Création du système de rendu de fallback...")
        
        # Créer une surface pour la carte
        self.fallback_map_surface = pygame.Surface((self.map_width, self.map_height))
        self.fallback_map_surface.fill((50, 150, 50))  # Fond vert
        
        # Rendre chaque couche
        for layer in self.tmx_data.layers:
            if not layer.visible:
                continue
                
            print(f"Rendu de la couche: {layer.name}")
            self._render_layer_fallback(layer)
        
        # Créer un groupe simple pour le joueur
        self.group = pygame.sprite.Group()
        print("Groupe de fallback créé")
    
    def _render_layer_fallback(self, layer):
        """Rend une couche avec le système de fallback"""
        if not hasattr(layer, 'data'):
            return
        
        # Couleurs pour différentes couches
        layer_colors = {
            'grass': (100, 255, 100),      # Vert herbe
            'murs': (150, 150, 150),       # Gris murs
            'pierres': (139, 69, 19)       # Marron pierres
        }
        
        base_color = layer_colors.get(layer.name, (128, 128, 128))
        
        # Rendre chaque tuile
        for y, row in enumerate(layer.data):
            for x, gid in enumerate(row):
                if gid != 0:  # Tuile non-vide
                    # Calculer la couleur basée sur le GID
                    color = self._get_tile_color_fallback(gid, layer.name, base_color)
                    
                    # Position de la tuile
                    tile_x = x * self.tmx_data.tilewidth
                    tile_y = y * self.tmx_data.tileheight
                    
                    # Dessiner la tuile
                    tile_rect = pygame.Rect(tile_x, tile_y, 
                                          self.tmx_data.tilewidth, 
                                          self.tmx_data.tileheight)
                    self.fallback_map_surface.fill(color, tile_rect)
                    
                    # Ajouter un contour pour certaines couches
                    if layer.name in ['murs', 'pierres']:
                        pygame.draw.rect(self.fallback_map_surface, (0, 0, 0), tile_rect, 1)
    
    def _get_tile_color_fallback(self, gid, layer_name, base_color):
        """Détermine la couleur d'une tuile pour le fallback"""
        # Créer des variations de couleur basées sur le GID
        variation = (gid % 50) * 2
        
        if layer_name == 'grass':
            # Variations de vert pour l'herbe
            return (
                max(0, min(255, base_color[0] + variation)),
                max(0, min(255, base_color[1] - variation // 2)),
                max(0, min(255, base_color[2] + variation // 3))
            )
        elif layer_name == 'murs':
            # Variations de gris pour les murs
            return (
                max(0, min(255, base_color[0] + variation)),
                max(0, min(255, base_color[1] + variation)),
                max(0, min(255, base_color[2] + variation))
            )
        elif layer_name == 'pierres':
            # Variations de marron pour les pierres
            return (
                max(0, min(255, base_color[0] + variation)),
                max(0, min(255, base_color[1] - variation // 2)),
                max(0, min(255, base_color[2] - variation // 3))
            )
        else:
            return base_color
    
    def _init_level(self):
        """Initialisation du niveau avec chargement TMX"""
        # Recherche du fichier TMX dans plusieurs emplacements possibles
        possible_paths = [
            'assets/maps/map.tmx',
            os.path.join(os.path.dirname(__file__), 'assets', 'maps', 'map.tmx'),
            os.path.join(os.path.dirname(__file__), 'assets', 'map.tmx'),
            os.path.join('assets', 'maps', 'map.tmx')
        ]
        
        tmx_path = None
        for path in possible_paths:
            if os.path.exists(path):
                tmx_path = path
                break
        
        if tmx_path:
            try:
                print(f"Chargement de la carte: {tmx_path}")
                
                # Chargement TMX
                self.tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
                print(f"TMX chargé - Dimensions: {self.tmx_data.width}x{self.tmx_data.height}")
                print(f"Taille des tuiles: {self.tmx_data.tilewidth}x{self.tmx_data.tileheight}")
                print(f"Nombre de couches: {len(self.tmx_data.layers)}")
                
                # Vérification des tilesets
                print(f"Nombre de tilesets: {len(self.tmx_data.tilesets)}")
                for i, tileset in enumerate(self.tmx_data.tilesets):
                    print(f"  Tileset {i}: {tileset.name}")
                    if hasattr(tileset, 'image') and tileset.image:
                        print(f"    Image: {tileset.image}")
                        if not os.path.exists(tileset.image):
                            print(f"    ERREUR: Image introuvable - {tileset.image}")
                            # Créer une image de fallback
                            self._create_fallback_tileset(tileset)
                    else:
                        print(f"    Pas d'image définie pour ce tileset")
                
                # Vérification des couches
                print(f"Vérification des couches:")
                for i, layer in enumerate(self.tmx_data.layers):
                    print(f"  Couche {i}: {layer.name} - Visible: {layer.visible}")
                    if hasattr(layer, 'data'):
                        non_zero_tiles = sum(1 for row in layer.data for tile in row if tile != 0)
                        print(f"    Tuiles non-vides: {non_zero_tiles}")
                
                # Calculer les dimensions de la carte
                self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
                self.map_height = self.tmx_data.height * self.tmx_data.tileheight
                
                # Forcer l'utilisation du système de fallback car les tilesets n'ont pas d'images
                print("Utilisation du système de fallback (tilesets sans images)...")
                self._create_fallback_renderer()
                
                print(f"Dimensions de la carte: {self.map_width}x{self.map_height}")
                
                self.map_loaded = True
                print("Carte chargée avec succès!")
                
            except Exception as e:
                print(f"Erreur lors du chargement de la carte: {e}")
                import traceback
                traceback.print_exc()
                self.error_message = str(e)
                self.map_loaded = False
        else:
            print("Aucun fichier TMX trouvé dans les emplacements suivants:")
            for path in possible_paths:
                print(f"  - {path}")
            self.error_message = "Fichier TMX introuvable"
            self.map_loaded = False

    def handle_event(self, event):
        """Gère les événements du jeu"""
        if event.type == pygame.KEYDOWN:
            # Gestion des touches spéciales
            if event.key == pygame.K_ESCAPE:
                return False  # Signal pour quitter
        return True
    
    def update(self):
        """Mise à jour des entités du jeu"""
        if not self.map_loaded:
            return
        
        # Gestion des entrées clavier pour le joueur
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        # Mise à jour du joueur avec limitation de la carte
        self.player.update(self.map_width, self.map_height)
        
        # Mise à jour de la caméra pour suivre le joueur
        self._update_camera()
        
        # Mise à jour du groupe pyscroll
        if self.group:
            self.group.update()
    
    def _update_camera(self):
        """Met à jour la position de la caméra pour suivre le joueur"""
        if not self.map_loaded or not self.player:
            return
        
        # Position du joueur au centre de l'écran
        target_x = self.player.rect.centerx - self.width // 2
        target_y = self.player.rect.centery - self.height // 2
        
        # Limitation de la caméra aux bords de la carte
        target_x = max(0, min(target_x, self.map_width - self.width))
        target_y = max(0, min(target_y, self.map_height - self.height))
        
        # Mise à jour de la position de la caméra
        self.camera_x = target_x
        self.camera_y = target_y
        
        # Application de la caméra au groupe pyscroll
        if self.group:
            self.group.center(self.player.rect.center)
    
    def render(self):
        """Rendu des entités du jeu"""
        if not self.map_loaded:
            self._render_error()
            return
        
        # Rendu de la carte
        if hasattr(self, 'fallback_map_surface'):
            # Utiliser le système de fallback
            self._render_fallback()
        else:
            # Utiliser pyscroll
            if self.group:
                self.group.draw(self.screen)
        
        # Rendu de l'interface utilisateur
        self._render_ui()
        
        pygame.display.flip()
    
    def _render_fallback(self):
        """Rend la carte avec le système de fallback"""
        # Calculer la position de la caméra
        camera_rect = pygame.Rect(self.camera_x, self.camera_y, self.width, self.height)
        
        # Dessiner la partie visible de la carte
        self.screen.blit(self.fallback_map_surface, (0, 0), camera_rect)
        
        # Dessiner le joueur
        if self.player:
            # Position du joueur relative à la caméra
            player_screen_x = self.player.rect.x - self.camera_x
            player_screen_y = self.player.rect.y - self.camera_y
            
            # Vérifier si le joueur est visible à l'écran
            if (0 <= player_screen_x < self.width and 
                0 <= player_screen_y < self.height):
                self.screen.blit(self.player.image, (player_screen_x, player_screen_y))
    
    def _render_error(self):
        """Rend l'écran d'erreur"""
        self.screen.fill((50, 50, 50))
        
        if self.error_message:
            error_text = self.font.render(f"Erreur: {self.error_message}", True, (255, 0, 0))
            text_rect = error_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(error_text, text_rect)
        
        pygame.display.flip()
    
    def _render_ui(self):
        """Rend l'interface utilisateur"""
        # Informations sur la position du joueur
        if self.player:
            pos_x, pos_y = self.player.get_position()
            pos_text = self.font.render(f"Position: ({int(pos_x)}, {int(pos_y)})", True, (255, 255, 255))
            self.screen.blit(pos_text, (10, 10))
        
        # Instructions de contrôle
        controls = [
            "Contrôles:",
            "WASD ou Flèches: Déplacer",
            "ÉCHAP: Quitter"
        ]
        
        for i, control in enumerate(controls):
            text = self.font.render(control, True, (255, 255, 255))
            self.screen.blit(text, (10, 40 + i * 25))