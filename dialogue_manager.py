import pygame
import json
import os

class DialogueManager:
    def __init__(self, font_path=None, font_size=18):
        self.font = pygame.font.Font(font_path, font_size)
        self.dialogues = {}
        self.active_scene = None
        self.current_line = 0
        self.is_active = False

    def load_from_file(self, filename):
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                self.dialogues.update(json.load(f))
            print(f"[DialogueManager] Dialogues chargés depuis {filename}: {list(self.dialogues.keys())}")
        else:
            print(f"[DialogueManager] Fichier introuvable : {filename}")

    def start_scene(self, scene_id):
        """Lance une séquence scénarisée (ex: 'scene_intro')"""
        if scene_id in self.dialogues:
            self.active_scene = scene_id
            self.current_line = 0
            self.is_active = True
        else:
            print(f"[DialogueManager] Aucune scène trouvée pour {scene_id}")

    def next_line(self):
        if not self.is_active:
            return
        self.current_line += 1
        if self.current_line >= len(self.dialogues[self.active_scene]):
            # Fin de la séquence
            self.is_active = False
            self.active_scene = None

    def draw(self, screen):
        if not self.is_active:
            return

        # Récupérer la réplique courante
        dialogue_entry = self.dialogues[self.active_scene][self.current_line]
        character = dialogue_entry.get("character", "???")
        line = dialogue_entry.get("line", "")

        # Surface pour le texte
        line_surface = self.font.render(line, True, (255, 255, 255))  
        character_surface = self.font.render(character + " :", True, (200, 200, 50))  

        # Dimensions de l'écran
        screen_width, screen_height = screen.get_size()
        
        # Taille de la boîte de dialogue
        padding = 20
        box_height = 140
        box_width = screen_width - 40
        
        # Position de la boîte
        box_x = 20
        box_y = screen_height - box_height - 20
        
        dialogue_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # Ombre
        shadow_rect = dialogue_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=15)
        
        # Boîte principale
        pygame.draw.rect(screen, (30, 30, 40), dialogue_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 100, 120), dialogue_rect, 3, border_radius=15)
        
        # Affichage du nom du personnage
        character_x = box_x + padding
        character_y = box_y + 10
        screen.blit(character_surface, (character_x, character_y))
        
        # Affichage de la ligne
        text_x = box_x + padding
        text_y = character_y + character_surface.get_height() + 10
        screen.blit(line_surface, (text_x, text_y))
        
        # Indicateur "Appuyer pour continuer"
        indicator_text = "Appuyez sur ESPACE pour continuer..."
        indicator_surface = pygame.font.Font(None, 16).render(indicator_text, True, (180, 180, 180))
        indicator_x = box_x + box_width - indicator_surface.get_width() - padding
        indicator_y = box_y + box_height - indicator_surface.get_height() - 10
        
        screen.blit(indicator_surface, (indicator_x, indicator_y))
