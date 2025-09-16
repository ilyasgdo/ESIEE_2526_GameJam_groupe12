#!/usr/bin/env python3
"""
Game Manager pour "Tu n'es pas le héros"
Gère les états du jeu, les entités et la logique principale
"""

import pygame
import sys
import os

class GameManager:
    """Gestionnaire principal du jeu"""
    
    def __init__(self, screen):
        """Initialisation du gestionnaire de jeu"""
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # États du jeu (selon le PRD)
        self.game_state = "LOBBY"  # LOBBY -> PREPARATION -> RUNNING -> RESULT
        
        # Couleurs de base
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        
        # Police pour l'interface
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Variables de jeu
        self.coins = 100  # Pièces du joueur
        self.hero_health = 100
        self.run_count = 0
        
        # Initialisation des composants
        self._init_level()
        self._init_ui()
    
    def _init_level(self):
        """Initialisation du niveau de base"""
        # Grille simple pour le niveau (20x15 cases)
        self.grid_width = 20
        self.grid_height = 15
        self.cell_size = 32
        
        # Position de départ et objectif
        self.hero_start = (1, 1)
        self.goal_position = (18, 13)
        
        # Position actuelle du héros
        self.hero_position = list(self.hero_start)
        
        # Pièges placés (dictionnaire position -> type)
        self.traps = {}
        
        # Danger map pour l'IA (selon le PRD)
        self.danger_map = {}
    
    def _init_ui(self):
        """Initialisation de l'interface utilisateur"""
        # Zone de jeu (centrée)
        self.game_area_x = (self.width - self.grid_width * self.cell_size) // 2
        self.game_area_y = (self.height - self.grid_height * self.cell_size) // 2
        
        # Zone d'interface
        self.ui_height = 100
        self.ui_y = self.height - self.ui_height
    
    def handle_event(self, event):
        """Gestion des événements"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._start_run()
            elif event.key == pygame.K_r:
                self._reset_game()
            elif event.key == pygame.K_s:
                self._enter_shop()
    
    def update(self):
        """Mise à jour de la logique du jeu"""
        if self.game_state == "RUNNING":
            self._update_hero_ai()
            self._check_goal_reached()
            self._check_traps()
    
    def render(self):
        """Rendu du jeu"""
        # Fond
        self.screen.fill(self.BLACK)
        
        # Rendu du niveau
        self._render_level()
        
        # Rendu de l'interface
        self._render_ui()
        
        # Rendu des informations de debug
        self._render_debug_info()
    
    def _render_level(self):
        """Rendu du niveau de base"""
        # Grille de fond
        for x in range(self.grid_width + 1):
            start_pos = (self.game_area_x + x * self.cell_size, self.game_area_y)
            end_pos = (self.game_area_x + x * self.cell_size, self.game_area_y + self.grid_height * self.cell_size)
            pygame.draw.line(self.screen, self.GRAY, start_pos, end_pos)
        
        for y in range(self.grid_height + 1):
            start_pos = (self.game_area_x, self.game_area_y + y * self.cell_size)
            end_pos = (self.game_area_x + self.grid_width * self.cell_size, self.game_area_y + y * self.cell_size)
            pygame.draw.line(self.screen, self.GRAY, start_pos, end_pos)
        
        # Position de départ (vert)
        start_rect = pygame.Rect(
            self.game_area_x + self.hero_start[0] * self.cell_size + 1,
            self.game_area_y + self.hero_start[1] * self.cell_size + 1,
            self.cell_size - 2,
            self.cell_size - 2
        )
        pygame.draw.rect(self.screen, self.GREEN, start_rect)
        
        # Objectif (rouge)
        goal_rect = pygame.Rect(
            self.game_area_x + self.goal_position[0] * self.cell_size + 1,
            self.game_area_y + self.goal_position[1] * self.cell_size + 1,
            self.cell_size - 2,
            self.cell_size - 2
        )
        pygame.draw.rect(self.screen, self.RED, goal_rect)
        
        # Héros (bleu)
        hero_rect = pygame.Rect(
            self.game_area_x + self.hero_position[0] * self.cell_size + 4,
            self.game_area_y + self.hero_position[1] * self.cell_size + 4,
            self.cell_size - 8,
            self.cell_size - 8
        )
        pygame.draw.rect(self.screen, self.BLUE, hero_rect)
        
        # Pièges (carrés rouges plus petits)
        for pos, trap_type in self.traps.items():
            trap_rect = pygame.Rect(
                self.game_area_x + pos[0] * self.cell_size + 8,
                self.game_area_y + pos[1] * self.cell_size + 8,
                self.cell_size - 16,
                self.cell_size - 16
            )
            pygame.draw.rect(self.screen, self.RED, trap_rect)
    
    def _render_ui(self):
        """Rendu de l'interface utilisateur"""
        # Fond de l'interface
        ui_rect = pygame.Rect(0, self.ui_y, self.width, self.ui_height)
        pygame.draw.rect(self.screen, (50, 50, 50), ui_rect)
        
        # Informations du jeu
        coins_text = self.font.render(f"Pièces: {self.coins}", True, self.WHITE)
        self.screen.blit(coins_text, (20, self.ui_y + 10))
        
        health_text = self.font.render(f"HP Héros: {self.hero_health}", True, self.WHITE)
        self.screen.blit(health_text, (20, self.ui_y + 50))
        
        state_text = self.font.render(f"État: {self.game_state}", True, self.WHITE)
        self.screen.blit(state_text, (300, self.ui_y + 10))
        
        # Instructions
        instructions = [
            "ESPACE: Démarrer le run",
            "R: Reset",
            "S: Shop",
            "ÉCHAP: Quitter"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.WHITE)
            self.screen.blit(text, (500, self.ui_y + 10 + i * 20))
    
    def _render_debug_info(self):
        """Rendu des informations de debug"""
        debug_info = [
            f"Position héros: {self.hero_position}",
            f"Run #{self.run_count}",
            f"Pièges actifs: {len(self.traps)}"
        ]
        
        for i, info in enumerate(debug_info):
            text = self.small_font.render(info, True, self.WHITE)
            self.screen.blit(text, (10, 10 + i * 20))
    
    def _start_run(self):
        """Démarre un run"""
        if self.game_state == "LOBBY" or self.game_state == "PREPARATION":
            self.game_state = "RUNNING"
            self.hero_position = list(self.hero_start)
            self.hero_health = 100
            self.run_count += 1
            print(f"Run #{self.run_count} démarré!")
    
    def _reset_game(self):
        """Remet à zéro le jeu"""
        self.game_state = "LOBBY"
        self.hero_position = list(self.hero_start)
        self.hero_health = 100
        self.traps.clear()
        print("Jeu remis à zéro")
    
    def _enter_shop(self):
        """Entre dans le shop"""
        if self.game_state == "LOBBY":
            self.game_state = "SHOP"
            print("Entrée dans le shop")
    
    def _update_hero_ai(self):
        """Mise à jour de l'IA du héros (mouvement simple)"""
        # IA simple : se déplacer vers l'objectif
        dx = 0
        dy = 0
        
        if self.hero_position[0] < self.goal_position[0]:
            dx = 1
        elif self.hero_position[0] > self.goal_position[0]:
            dx = -1
        
        if self.hero_position[1] < self.goal_position[1]:
            dy = 1
        elif self.hero_position[1] > self.goal_position[1]:
            dy = -1
        
        # Mise à jour de la position
        new_x = max(0, min(self.grid_width - 1, self.hero_position[0] + dx))
        new_y = max(0, min(self.grid_height - 1, self.hero_position[1] + dy))
        
        self.hero_position = [new_x, new_y]
    
    def _check_goal_reached(self):
        """Vérifie si le héros a atteint l'objectif"""
        if self.hero_position == list(self.goal_position):
            self.game_state = "RESULT"
            self.coins += 5  # Gain pour réussite
            print("Objectif atteint! +5 pièces")
    
    def _check_traps(self):
        """Vérifie les collisions avec les pièges"""
        hero_pos_tuple = tuple(self.hero_position)
        if hero_pos_tuple in self.traps:
            # Piège déclenché
            self.hero_health = 0
            self.game_state = "RESULT"
            self.coins += 10  # Gain pour mort du héros
            print("Héros tué par piège! +10 pièces")
