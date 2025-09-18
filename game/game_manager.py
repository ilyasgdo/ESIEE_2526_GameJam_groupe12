#!/usr/bin/env python3
"""
Game Manager pour "Tu n'es pas le héros"
Version simplifiée - chargement de map uniquement avec diagnostics
"""

import pygame
import os
import pytmx
import pyscroll

from actions.actions import TAB_ACTION
from actions.bomb import Bomb
from actions.trap import Trap
from game.dialogue_manager import DialogueManager
from actions.fire_ball import FireBall
from player.player import Player
from hero_bot.bot import Bot
from Allierbot.ally_bot import AllyBot
from interface.minimap import Minimap
from game.formation_manager import FormationManager
from interface.UIManager import UIManager

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
        self.dialogue_manager = DialogueManager()
        self.dialogue_manager.load_from_file("assets/dialogues/scenes.json")
        self.fireballs = pygame.sprite.Group()
        self.last_shot_time = 0
        self.last_placed_trap = 0
        self.last_placed_bomb = 0

        # Créer le bot allié avec position initiale spécifique
        ally_spawn_x = 786.67
        ally_spawn_y = 5900.67
        self.ally_bot = AllyBot(ally_spawn_x, ally_spawn_y, self.player)
        self.group.add(self.ally_bot)
        self.percentage = 50.0  # Pourcentage initial de 50%
        self.score = 0
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
        
        # Établir la référence bidirectionnelle entre ally_bot et bot pour la détection de proximité
        self.ally_bot.set_bot_reference(self.bot)
        
        # Configurer les objets de collision pour tous les bots
        self.ally_bot.set_collision_objects(self.collisions)
        self.bot.set_collision_objects(self.collisions)
        
        # Configurer les objets de collision pour tous les subordonnés
        for subordinate in self.formation_manager.get_subordinates():
            subordinate.set_collision_objects(self.collisions)
        
        # Créer la minimap
        self.minimap = Minimap(self.screen, self.tmx_data, x=10, y=10, width=200, height=150)

        # Créer l'UI Manager et initialiser les variables d'état
        self.ui = UIManager(screen.get_size())
        self.input_locked_for_ui = False  # si True, ignorer input joueur, CINEMATIQUE

        pygame.display.flip()
    
    def _init_level(self):
        """Initialisation du niveau avec chargement TMX"""
        # Recherche du fichier TMX dans plusieurs emplacements possibles
        possible_paths = [
            'assets/maps/map.tmx',
            os.path.join(os.path.dirname(__file__), 'assets', 'maps', 'map.tmx'),
            os.path.join(os.path.dirname(__file__), 'assets', 'map.tmx'),
            os.path.join('../assets', 'maps', 'map.tmx')
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

    def get_percentage(self):
        """Retourne le pourcentage actuel"""
        return self.percentage

    def get_score(self):
        """Retourne le score actuel"""
        return self.score

    def update(self):
        """Mise à jour des entités du jeu"""
        self.group.update()
        self.group.center(self.player.rect.center)
        self.fireballs.update()
        # Vérifier les collisions projectile-héros
        self.check_projectile_hero_collision()
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
        # Mise à jour de l'UI (timers, animations UI)
        self.ui.update()
        
    def check_projectile_hero_collision(self):
            """Vérifie les collisions entre les projectiles et le héros (bot)"""
            if not hasattr(self, 'bot') or not self.bot:
                return
            
            if not hasattr(self, 'fireballs') or not self.fireballs:
                return
            
            # Collision avec le bot principal (héros) - détruit le projectile automatiquement
            collisions = pygame.sprite.spritecollide(self.bot, self.fireballs, True)
            
            for fireball in collisions:
                # Augmenter le pourcentage de 0.5%
                self.percentage += fireball.damage
                # Plafonner le pourcentage à 100% si nécessaire
                if self.percentage > 100.0:
                    self.percentage = 100.0
                
                # Augmenter le score
                self.score += fireball.score
                
                # Message de debug
                print(f"💥 Héros touché! Pourcentage: {self.percentage:.1f}% - Score: {self.score}")
                
                # Effet visuel/sonore optionnel (peut être ajouté plus tard)
                self.on_hero_hit()

    def on_hero_hit(self):
        """Appelé quand le héros est touché - pour effets supplémentaires"""
        # Ici on peut ajouter des effets visuels, sons, etc.
        # Pour l'instant, juste un feedback console
        if self.percentage >= 100.0:
            print("🎉 POURCENTAGE MAXIMUM ATTEINT! (100%)")
        elif self.percentage >= 75.0:
            print("⭐ Excellent! Pourcentage élevé!")
        elif self.percentage >= 60.0:
            print("👍 Bon travail!")
    
    def reset_percentage(self):
        """Remet le pourcentage à 50% (méthode utilitaire)"""
        self.percentage = 50.0
        print(f"Pourcentage remis à {self.percentage}%")
    
    def add_percentage_bonus(self, bonus):
        """Ajoute un bonus de pourcentage (méthode utilitaire)"""
        old_percentage = self.percentage
        self.percentage += bonus
        if self.percentage > 100.0:
            self.percentage = 100.0
        print(f"Bonus de {bonus}%! Pourcentage: {old_percentage:.1f}% → {self.percentage:.1f}%")


    def render(self):
        """Rendu des entités du jeu"""
        if not self.dialogue_manager.is_active():
            self.group.draw(self.screen)
            self.fireballs.draw(self.screen)
            # Rendre la minimap par-dessus le jeu
            if hasattr(self, 'minimap'):
                self.minimap.render()
            self.ui.render(self.screen)
        self.dialogue_manager.draw(self.screen)

        pygame.display.flip()


    def handle_movent(self, pressed):
        self.player.save_location()
        is_moving = False
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

        self.player.reset_movement_flags()
        if pressed[pygame.K_z]: self.player.movement_directions['up'] = True
        if pressed[pygame.K_s]: self.player.movement_directions['down'] = True
        if pressed[pygame.K_q]: self.player.movement_directions['left'] = True
        if pressed[pygame.K_d]: self.player.movement_directions['right'] = True

    def handle_collision(self):
        for obj in self.collisions:
            top_left = (obj.x, obj.y)
            bottom_left = (obj.x, obj.y + obj.height)
            top_right = (obj.x + obj.width, obj.y)
            bottom_right = (obj.x + obj.width, obj.y + obj.height)
            player_position = self.player.position
            # print(top_left, bottom_left, top_right, bottom_right)

            if (player_position[0] >= top_left[0] and player_position[1] >= top_left[1]) and (
                    player_position[0] >= bottom_left[0] and player_position[1] <= bottom_left[1]) and (
                    player_position[0] <= top_right[0] and player_position[1] >= top_right[1]) and (
                    player_position[0] <= bottom_right[0] and player_position[1] <= bottom_right[1]):
                self.player.move_player_back()


    def can_place_action(self, now, last, countdown):
        if now - last >= countdown:
            return True
        return False

    def get_now(self):
        return pygame.time.get_ticks()

    def handle_fireballs(self):
        now = self.get_now()
        fireball = FireBall(
            self.player.position[0] + 16,  # centre du sprite joueur
            self.player.position[1] + 16,
            self.player.last_direction
        )
        if self.can_place_action(now, self.last_shot_time, fireball.countdown):
            self.ui.activate_hotbar_slot(0, fireball.countdown/1000)

            self.fireballs.add(fireball)
            self.group.add(fireball)  # pyscroll la gère
            self.last_shot_time = now

    def handle_trap(self, x, y):
        now = self.get_now()
        trap = Trap(x, y)
        if self.can_place_action(now, self.last_placed_trap, trap.countdown):
            TAB_ACTION.append(trap)
            self.ui.activate_hotbar_slot(1, trap.countdown/1000)
            self.group.add(trap)
            self.last_placed_trap = now
            self.score += trap.score

    def handle_bomb(self, x, y):
        now = self.get_now()
        bomb = Bomb(x, y)
        if self.can_place_action(now, self.last_placed_bomb, bomb.countdown):
            TAB_ACTION.append(bomb)
            self.ui.activate_hotbar_slot(3, bomb.countdown / 1000)
            self.group.add(bomb)
            self.last_placed_trap = now
            self.score += bomb.score

    def handle_action(self, pressed):
        #Ajouter les autres actions
        # faire changer le countdown via cette fonction

        x = self.player.position[0]
        y = self.player.position[1]

        if pressed[pygame.K_SPACE]: # fireBall
           self.handle_fireballs()
        elif pressed[pygame.K_g]:
            self.handle_trap(x, y)
        elif pressed[pygame.K_h]:
            self.ui.activate_hotbar_slot(2, 20)
        elif pressed[pygame.K_j]:
            self.handle_bomb(x, y)
        elif pressed[pygame.K_o]:
            self.ui.start_stun(2.5)
        elif pressed[pygame.K_SPACE]:
            # Déléguer la gestion du dialogue au GameManager
            self.handle_dialogue()

    def handle_input(self):
        pressed = pygame.key.get_pressed()

        self.handle_movent(pressed)
        self.handle_collision()
        self.handle_action(pressed)





    def handle_dialogue(self):
        """Gérer le passage au dialogue suivant ou démarrer un dialogue"""
        if self.dialogue_manager.is_active:
            self.dialogue_manager.next_line()
        else:
            self.dialogue_manager.start_scene("scene_intro")
