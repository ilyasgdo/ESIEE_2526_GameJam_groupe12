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
from bot import Bot
from ally_bot import AllyBot
from minimap import Minimap
from formation_manager import FormationManager

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
        # Initialisation du niveau
        self._init_level()
        self.group.draw(self.screen)
        player_position = self.spawn_position
        self.player = Player(player_position.x, player_position.y)

        self.group.add(self.player)
        
        # Créer le bot allié qui se déplace vers le haut - spawn près du joueur
        ally_spawn_x = player_position.x + 30  # Spawn près du joueur
        ally_spawn_y = player_position.y + 30
        self.ally_bot = AllyBot(ally_spawn_x, ally_spawn_y)
        self.group.add(self.ally_bot)
        
        # Définir la référence au bot allié pour le joueur (contrainte de distance)
        self.player.set_ally_bot(self.ally_bot)
        
        # Créer le gestionnaire de formation avec 5 subordonnés
        self.formation_manager = FormationManager(self.ally_bot)
        
        # Ajouter tous les subordonnés au groupe de sprites
        for subordinate in self.formation_manager.get_subordinates():
            self.group.add(subordinate)
        
        # Créer le bot qui suit le joueur - spawn en bas à gauche de la carte
        bot_spawn_x = 100  # Position proche du bord gauche
        bot_spawn_y = (self.tmx_data.height * self.tmx_data.tileheight) - 100  # Position proche du bord bas
        self.bot = Bot(bot_spawn_x, bot_spawn_y, self.ally_bot)  # Le bot suit maintenant l'ally_bot
        self.group.add(self.bot)
        
        # Créer la minimap
        self.minimap = Minimap(self.screen, self.tmx_data, x=10, y=10, width=200, height=150)

        # centrer la camera sur le joueur


        pygame.display.flip()
    
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
                tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
                self.tmx_data = tmx_data
                self.spawn_position = tmx_data.get_object_by_name("player_spawn")

                self.collisions = []
                for obj in tmx_data.objects:
                    if obj.name == "collision":
                        self.collisions.append(obj)

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
                
                # Création des données pyscroll
                map_data = pyscroll.data.TiledMapData(self.tmx_data)
                print("Données pyscroll créées")
                
                # Création du renderer
                map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
                print("Renderer créé")
                map_layer.zoom = 2.0
                # Création du groupe
                self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=3)
                print("Groupe pyscroll créé")
                
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

    def update(self):
        """Mise à jour des entités du jeu"""
        self.group.update()
        self.group.center(self.player.rect.center)
        
        # Mettre à jour le gestionnaire de formation
        if hasattr(self, 'formation_manager'):
            self.formation_manager.update()
        
        # Mettre à jour la minimap avec les positions des entités
        if hasattr(self, 'minimap') and self.minimap:
            self.minimap.update_player_position(self.player.position[0], self.player.position[1])
            self.minimap.update_ally_position(self.ally_bot.position[0], self.ally_bot.position[1])
            
            # Mettre à jour la position du bot
            if hasattr(self, 'bot') and self.bot:
                self.minimap.update_bot_position(self.bot.position[0], self.bot.position[1])
            
            # Mettre à jour les positions des subordonnés
            if hasattr(self, 'formation_manager'):
                self.minimap.update_subordinates_positions(self.formation_manager.get_subordinates())
            
            # Appeler la méthode update pour rafraîchir l'affichage
            self.minimap.update()


    def render(self):
        """Rendu des entités du jeu"""
        self.group.draw(self.screen)
        
        # Rendre la minimap par-dessus le jeu
        if hasattr(self, 'minimap'):
            self.minimap.render()
            
        pygame.display.flip()

    def handle_input(self):
        pressed = pygame.key.get_pressed()
        is_moving = False
        
        # Réinitialiser l'état de mouvement du joueur
        self.player.stop()

        self.player.save_location()

        if pressed[pygame.K_z]:
            self.player.move_up()
            is_moving = True
        if pressed[pygame.K_s]:
            self.player.move_down()
            is_moving = True
        if pressed[pygame.K_q]:
            self.player.move_left()
            is_moving = True
        if pressed[pygame.K_d]:
            self.player.move_right()
            is_moving = True
        if not is_moving:
            self.player.stop()

