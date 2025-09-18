#!/usr/bin/env python3
"""
Game Manager pour "Tu n'es pas le héros"
Version simplifiée - chargement de map uniquement avec diagnostics
"""

import pygame
import os
import pytmx
import pyscroll
import random

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
from game.music_game import MusicGame
from interface.movement_zone_renderer import MovementZoneRenderer


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

        # Musique
        self.music = MusicGame(music_volume=0.5)

        # Initialisation du niveau
        self._init_level()
        self.group.draw(self.screen)
        player_position = self.spawn_position
        self.player = Player(player_position.x, player_position.y)

        self.player = Player(player_position.x, player_position.y)
        self.player.set_audio(self.music)

        self.group.add(self.player)
        self.dialogue_manager = DialogueManager()
        self.dialogue_manager.load_from_file("assets/dialogues/scenes.json")
        self.fireballs = pygame.sprite.Group()
        self.last_shot_time = -1
        self.last_placed_trap = -1
        self.last_placed_bomb = -1


        # Créer le bot allié avec position initiale spécifique
        ally_spawn_x = 786.67
        ally_spawn_y = 5900.67
        self.ally_bot = AllyBot(ally_spawn_x, ally_spawn_y, self.player)
        self.group.add(self.ally_bot)
        self.percentage = 50.0  # Pourcentage initial de 50%
        self.score = 0

        # Variables pour l'écran de fin
        self.game_ended = False
        self.end_screen_result = None  # 'victory' ou 'defeat'
        self.end_screen_timer = 0
        self.end_screen_duration = 5000  # 5 secondes en millisecondes
        self.should_quit = False  # Flag pour indiquer qu'il faut quitter le jeu
        
        # Zone de téléportation (rectangle défini par les coordonnées fournies)
        self.teleport_zone = {
            'x1': 285.67,  # Coin gauche
            'y1': 677.67,  # Coin haut
            'x2': 999.67,  # Coin droit
            'y2': 908.67   # Coin bas
        }
        
        # Positions de téléportation
        self.teleport_positions = {
            'ally_bot': (567.67, 284.67),
            'bot': (735.67, 284.67),
            'player': (651.67, 284.67)  # Position centrale entre les deux bots
        }
        
        # Flag pour éviter les téléportations multiples
        self.teleported = False
        
        # Variables pour le délai avant l'écran de fin
        self.teleport_time = None
        self.end_screen_delay = 3000  # 3 secondes en millisecondes
        self.player.set_ally_bot(self.ally_bot)
        
        # Créer le gestionnaire de formation avec 5 subordonnés
        self.formation_manager = FormationManager(self.ally_bot)
        
        # Ajouter tous les subordonnés au groupe de sprites
        for subordinate in self.formation_manager.get_subordinates():
            self.group.add(subordinate)
        
        # Créer le bot qui suit le joueur - spawn en bas à gauche de la carte
        bot_spawn_x = 100  # Position proche du bord gauche
        bot_spawn_y = (self.tmx_data.height * self.tmx_data.tileheight) - 100  # Position proche du bord bas
        self.bot = Bot(bot_spawn_x, bot_spawn_y, self.ally_bot, self)  # Le bot suit maintenant l'ally_bot
        self.group.add(self.bot)
        
        # Établir la référence bidirectionnelle entre ally_bot et bot pour la détection de proximité
        self.ally_bot.set_bot_reference(self.bot)
        
        # Établir la référence du hero bot pour que l'ally bot puisse lui tirer dessus
        self.ally_bot.set_hero_bot_reference(self.bot)
        
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
        
        # Créer le renderer de zone de mouvement
        self.movement_zone_renderer = MovementZoneRenderer()

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

                # Démarrer la musique de fond
                self.music.play_music('assets/musics/game_music.ogg', loop=-1, volume=0.2, fade_in=1000)

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

    def trigger_end_screen(self):
        """Déclenche l'écran de fin avec un résultat aléatoire (méthode legacy)"""
        if not self.game_ended:
            self.game_ended = True
            # Random entre victoire et défaite (50/50)
            self.end_screen_result = random.choice(['victory', 'defeat'])
            self.end_screen_timer = pygame.time.get_ticks()
            
            # Activer les barres cinématiques
            self.ui.show('cinematic_bars')
            
            # Messages selon le résultat
            if self.end_screen_result == 'victory':
                print("🎉 VICTOIRE DU MÉCHANT! Le héros a été vaincu!")
                message = "VICTOIRE! Le méchant triomphe!"
            else:
                print("😔 DÉFAITE DU MÉCHANT! Le héros l'a emporté...")
                message = "DÉFAITE! Le héros a gagné..."
            
            # Afficher le message dans l'UI
            self.ui.show('dialog', message)

    def trigger_end_screen_with_percentage(self):
        """Déclenche l'écran de fin basé sur le pourcentage de victoire de l'ally bot"""
        if not self.game_ended:
            self.game_ended = True
            self.end_screen_timer = pygame.time.get_ticks()
            
            # Activer les barres cinématiques
            self.ui.show('cinematic_bars')
            
            # Déterminer le résultat basé sur le pourcentage
            # Si le pourcentage est >= 60%, c'est une victoire, sinon défaite
            if self.percentage >= 70:
                self.end_screen_result = 'victory'
                print(f"🎉 VICTOIRE DU MÉCHANT! Pourcentage final: {self.percentage:.1f}% - Score: {self.score}")
                message = f"VICTOIRE! Le méchant triomphe!\nPourcentage: {self.percentage:.1f}% - Score: {self.score}"
            else:
                self.end_screen_result = 'defeat'
                print(f"😔 DÉFAITE DU MÉCHANT! Pourcentage final: {self.percentage:.1f}% - Score: {self.score}")
                message = f"DÉFAITE! Le héros a gagné...\nPourcentage: {self.percentage:.1f}% - Score: {self.score}"
            
            # Afficher le message dans l'UI
            self.ui.show('dialog', message)

    def get_percentage(self):
        """Retourne le pourcentage actuel"""
        return self.percentage

    def get_score(self):
        """Retourne le score actuel"""
        return self.score

    def update(self):
        """Mise à jour des entités du jeu"""
        if self.game_ended:
            current_time = pygame.time.get_ticks()
            if current_time - self.end_screen_timer >= self.end_screen_duration:
                print("🚪 Fermeture automatique du jeu après l'écran de fin...")
                self.should_quit = True
                return
        
        if not self.game_ended:
            self.group.update()
            self.group.center(self.player.rect.center)
            self.fireballs.update()
            
            # Vérifier les collisions projectile-héros
            self.check_projectile_hero_collision()
            
            # Vérifier la zone de téléportation
            self.check_teleport_zone()
            
            # Vérifier si le délai après téléportation est écoulé
            if self.teleported and self.teleport_time is not None:
                current_time = pygame.time.get_ticks()
                if current_time - self.teleport_time >= self.end_screen_delay:
                    print("⏰ Délai écoulé, déclenchement de l'écran de fin!")
                    self.trigger_end_screen_with_percentage()
                    self.teleport_time = None  # Réinitialiser pour éviter les appels multiples
            
            # Mettre à jour le gestionnaire de formation avec les groupes de projectiles
            if hasattr(self, 'formation_manager'):
                self.formation_manager.update(self.fireballs, self.group)
            
            # Appeler la méthode update pour rafraîchir l'affichage
            self.minimap.update()
            # Mise à jour de l'UI (timers, animations UI)
            self.ui.percentage_value = self.percentage  

            # Mettre à jour l'ally bot avec les groupes de projectiles pour le tir sur le hero bot
            if hasattr(self, 'ally_bot'):
                self.ally_bot.update(self.fireballs, self.group)
            
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

    def is_in_teleport_zone(self, x, y):
        """Vérifie si une position est dans la zone de téléportation"""
        return (self.teleport_zone['x1'] <= x <= self.teleport_zone['x2'] and
                self.teleport_zone['y1'] <= y <= self.teleport_zone['y2'])

    def check_teleport_zone(self):
        """Vérifie si les bots ou le joueur sont dans la zone de téléportation et les téléporte si nécessaire"""
        if self.teleported or self.game_ended:
            return
        
        # Vérifier si l'ally bot est dans la zone
        ally_in_zone = self.is_in_teleport_zone(self.ally_bot.position[0], self.ally_bot.position[1])
        
        # Vérifier si le bot est dans la zone
        bot_in_zone = self.is_in_teleport_zone(self.bot.position[0], self.bot.position[1])
        
        # Vérifier si le joueur est dans la zone
        player_in_zone = self.is_in_teleport_zone(self.player.position[0], self.player.position[1])
        
        # Si au moins un des trois est dans la zone, téléporter tous
        if ally_in_zone or bot_in_zone or player_in_zone:
            print("🌟 Zone de téléportation activée! Téléportation de tous les personnages...")
            
            # Téléporter l'ally bot
            ally_pos = self.teleport_positions['ally_bot']
            self.ally_bot.position[0] = ally_pos[0]
            self.ally_bot.position[1] = ally_pos[1]
            self.ally_bot.rect.center = (int(ally_pos[0]), int(ally_pos[1]))
            
            # Téléporter le bot
            bot_pos = self.teleport_positions['bot']
            self.bot.position[0] = bot_pos[0]
            self.bot.position[1] = bot_pos[1]
            self.bot.rect.center = (int(bot_pos[0]), int(bot_pos[1]))
            
            # Téléporter le joueur
            player_pos = self.teleport_positions['player']
            self.player.position[0] = player_pos[0]
            self.player.position[1] = player_pos[1]
            self.player.rect.center = (int(player_pos[0]), int(player_pos[1]))
            
            # Marquer comme téléporté pour éviter les téléportations multiples
            self.teleported = True
            
            # Enregistrer le temps de téléportation pour le délai
            self.teleport_time = pygame.time.get_ticks()
            
            print(f"✅ Ally bot téléporté à: ({ally_pos[0]}, {ally_pos[1]})")
            print(f"✅ Bot téléporté à: ({bot_pos[0]}, {bot_pos[1]})")
            print(f"✅ Joueur téléporté à: ({player_pos[0]}, {player_pos[1]})")
            print("⏳ Attente de 3 secondes avant l'écran de fin...")


    def render(self):
        """Rendu avec gestion de l'écran de fin - VERSION CORRIGÉE"""
        if self.game_ended:
            # Rendu normal du jeu en arrière-plan (optionnel)
            self.group.draw(self.screen)
            self.fireballs.draw(self.screen)
            
            # Rendre la minimap par-dessus le jeu
            if hasattr(self, 'minimap'):
                self.minimap.render()
            
            # Fond sombre pour l'écran de fin
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            # Afficher le texte de fin
            font_large = pygame.font.Font(None, 72)
            font_medium = pygame.font.Font(None, 48)
            
            if self.end_screen_result == 'victory':
                title_color = (255, 215, 0)  # Or pour victoire
                title_text = "VICTOIRE!"
                subtitle_text = "Le méchant triomphe!"
            else:
                title_color = (220, 20, 60)  # Rouge pour défaite
                title_text = "DÉFAITE!"
                subtitle_text = "Le héros a gagné..."
            
            # Titre principal
            title_surface = font_large.render(title_text, True, title_color)
            title_rect = title_surface.get_rect(center=(self.width//2, self.height//2 - 50))
            self.screen.blit(title_surface, title_rect)
            
            # Sous-titre
            subtitle_surface = font_medium.render(subtitle_text, True, (255, 255, 255))
            subtitle_rect = subtitle_surface.get_rect(center=(self.width//2, self.height//2 + 20))
            self.screen.blit(subtitle_surface, subtitle_rect)
            
            # Score final
            score_text = f"Score final: {self.score}"
            percentage_text = f"Pourcentage: {self.percentage:.1f}%"
            
            font_small = pygame.font.Font(None, 36)
            score_surface = font_small.render(score_text, True, (200, 200, 200))
            percentage_surface = font_small.render(percentage_text, True, (200, 200, 200))
            
            score_rect = score_surface.get_rect(center=(self.width//2, self.height//2 + 80))
            percentage_rect = percentage_surface.get_rect(center=(self.width//2, self.height//2 + 120))
            
            self.screen.blit(score_surface, score_rect)
            self.screen.blit(percentage_surface, percentage_rect)
            
            # Timer de fin
            remaining_time = max(0, (self.end_screen_duration - (pygame.time.get_ticks() - self.end_screen_timer)) // 1000)
            timer_text = f"Redémarrage dans {remaining_time + 1}s..."
            timer_surface = font_small.render(timer_text, True, (150, 150, 150))
            timer_rect = timer_surface.get_rect(center=(self.width//2, self.height//2 + 180))
            self.screen.blit(timer_surface, timer_rect)
            
            # Instructions
            instruction_text = "Appuyez sur ESPACE pour redémarrer immédiatement"
            instruction_surface = pygame.font.Font(None, 24).render(instruction_text, True, (120, 120, 120))
            instruction_rect = instruction_surface.get_rect(center=(self.width//2, self.height//2 + 220))
            self.screen.blit(instruction_surface, instruction_rect)
            
        else:
            # Rendu normal du jeu
            if not self.dialogue_manager.is_active():
                self.group.draw(self.screen)
                self.fireballs.draw(self.screen)
                # Rendre la minimap par-dessus le jeu
                if hasattr(self, 'minimap'):
                    self.minimap.render()
                self.ui.render(self.screen)
                # Rendre la zone de mouvement du joueur autour de l'ally bot
                self.movement_zone_renderer.render_movement_zone(
                    self.screen, 
                    self.player, 
                    self.ally_bot
                )
                
                # Rendre les informations de distance
                self.movement_zone_renderer.render_distance_info(
                    self.screen, 
                    self.player
                )
            
            # TOUJOURS dessiner les dialogues en dernier (par-dessus tout)
            self.dialogue_manager.draw(self.screen)

        # IMPORTANT : Toujours faire le flip à la fin
        pygame.display.flip()

    def reset_game(self):
        """Remet le jeu à zéro après l'écran de fin"""
        self.game_ended = False
        self.end_screen_result = None
        self.percentage = 50.0
        self.score = 0
        
        # Réinitialiser le flag de téléportation
        self.teleported = False
        self.teleport_time = None
        
        # Cacher les éléments UI de fin
        self.ui.hide('cinematic_bars')
        self.ui.hide('dialog')
        
        # Repositionner les entités
        if hasattr(self, 'player'):
            self.player.position = [self.spawn_position.x, self.spawn_position.y]
        
        if hasattr(self, 'ally_bot'):
            self.ally_bot.position = [786.67, 5900.67]
        
        if hasattr(self, 'bot'):
            bot_spawn_x = 100
            bot_spawn_y = (self.tmx_data.height * self.tmx_data.tileheight) - 100
            self.bot.position = [bot_spawn_x, bot_spawn_y]
        
        # Vider les projectiles
        if hasattr(self, 'fireballs'):
            self.fireballs.empty()
        
        print("🔄 Jeu redémarré!")

    def handle_movent(self, pressed):
        self.player.save_location()
        is_moving = False

        # Reset flags avant d'assigner
        self.player.reset_movement_flags()

        # --- Déplacement ---
        if pressed[pygame.K_z]:
            self.player.move_up()
            self.player.movement_directions['up'] = True
            is_moving = True
        if pressed[pygame.K_s]:
            self.player.move_down()
            self.player.movement_directions['down'] = True
            is_moving = True
        if pressed[pygame.K_q]:
            self.player.move_left()
            self.player.movement_directions['left'] = True
            is_moving = True
        if pressed[pygame.K_d]:
            self.player.move_right()
            self.player.movement_directions['right'] = True
            is_moving = True

        # --- Animation avec priorité ---
        if pressed[pygame.K_z]:
            self.player.current_anim = "up"
        elif pressed[pygame.K_s]:
            self.player.current_anim = "down"
        elif pressed[pygame.K_q]:
            self.player.current_anim = "left"
        elif pressed[pygame.K_d]:
            self.player.current_anim = "right"
        # Si aucune touche n'est pressée, on garde l'animation précédente jusqu'au stop()

        if not is_moving:
            self.player.stop()



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
        if last == -1:
            return True
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
            self.last_shot_time = self.get_now()

    def handle_trap(self, x, y):
        now = self.get_now()
        trap = Trap(x, y)
        if self.can_place_action(now, self.last_placed_trap, trap.countdown):
            TAB_ACTION.append(trap)
            self.ui.activate_hotbar_slot(1, trap.countdown/1000)
            self.group.add(trap)
            self.last_placed_trap = self.get_now()
            self.score += 10
            self.score += trap.score

    def handle_bomb(self, x, y):
        now = self.get_now()
        bomb = Bomb(x, y)
        if self.can_place_action(now, self.last_placed_bomb, bomb.countdown):
            TAB_ACTION.append(bomb)
            self.ui.activate_hotbar_slot(2, bomb.countdown / 1000)
            self.group.add(bomb)
            self.last_placed_bomb = self.get_now()
            self.score += bomb.score

    def handle_action(self, pressed):
        #Ajouter les autres actions
        # faire changer le countdown via cette fonction
        if self.game_ended:
            return
        x = self.player.position[0]
        y = self.player.position[1]

        if pressed[pygame.K_SPACE]:  # fireBall
            self.handle_fireballs()
        elif pressed[pygame.K_g]:
            self.handle_trap(x, y)
        elif pressed[pygame.K_h]:
            self.handle_bomb(x, y)
        elif pressed[pygame.K_SPACE]:
            # Déléguer la gestion du dialogue au GameManager
            self.handle_dialogue()

    def handle_input(self):
        pressed = pygame.key.get_pressed()
        if self.game_ended:
            # Pendant l'écran de fin, on peut permettre d'accélérer avec ESPACE
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_SPACE]:
                self.reset_game()
            return
        self.handle_movent(pressed)
        self.handle_collision()
        self.handle_action(pressed)

    def handle_dialogue(self):
        """Gérer le passage au dialogue suivant ou démarrer un dialogue"""
        if self.dialogue_manager.is_active:
            self.dialogue_manager.next_line()
        else:
            self.dialogue_manager.start_scene("scene_intro")
    def check_win_lose_conditions(self):
            """Vérifie automatiquement les conditions de fin de partie"""
            # Exemple de conditions automatiques (à adapter selon votre jeu)
            
            # Victoire automatique si pourcentage >= 100%
            if self.percentage >= 100.0:
                if not self.game_ended:
                    # Forcer une victoire si le pourcentage est au max
                    self.game_ended = True
                    self.end_screen_result = 'victory'
                    self.end_screen_timer = pygame.time.get_ticks()
                    self.ui.show('cinematic_bars')
                    self.ui.show('dialog', "VICTOIRE PARFAITE! 100% atteint!")
            
            # Défaite si le héros (bot) atteint une certaine zone
            # (exemple : si le bot atteint les coordonnées du joueur)
            if hasattr(self, 'bot') and hasattr(self, 'player'):
                distance = ((self.bot.position[0] - self.player.position[0])**2 + 
                        (self.bot.position[1] - self.player.position[1])**2)**0.5
                if distance < 50:  # Distance très proche
                    if not self.game_ended:
                        self.game_ended = True
                        self.end_screen_result = 'defeat'
                        self.end_screen_timer = pygame.time.get_ticks()
                        self.ui.show('cinematic_bars')
                        self.ui.show('dialog', "Le héros vous a rattrapé!")