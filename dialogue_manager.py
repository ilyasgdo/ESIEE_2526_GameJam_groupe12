import pygame
import json
import os

class DialogueManager:
    def __init__(self, font_path=None, font_size=18):
        self.font = pygame.font.Font(font_path, font_size)
        self.dialogues = {}
        self.active_dialogue = None
        self.current_line = 0
        self.is_active = False

    def load_from_file(self, filename):
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                self.dialogues.update(json.load(f))
            print(f"[DialogueManager] Dialogues chargés depuis {filename}: {list(self.dialogues.keys())}")
        else:
            print(f"[DialogueManager] Fichier introuvable : {filename}")

    def start(self, npc_id):
        if npc_id in self.dialogues:
            self.active_dialogue = npc_id
            self.current_line = 0
            self.is_active = True
        else:
            print(f"[DialogueManager] Aucun dialogue trouvé pour {npc_id}")

    def next_line(self):
        if not self.is_active:
            return
        self.current_line += 1
        if self.current_line >= len(self.dialogues[self.active_dialogue]):
            self.is_active = False
            self.active_dialogue = None

    def draw(self, screen):
        if not self.is_active:
            return

        text = self.dialogues[self.active_dialogue][self.current_line]
        text_surface = self.font.render(text, True, (255, 255, 255))  # texte blanc

        # Dimensions de l'écran
        screen_width, screen_height = screen.get_size()
        
        # Taille de la boîte de dialogue
        padding = 20
        box_height = 120
        box_width = screen_width - 40  # Marges de 20px de chaque côté
        
        # Position de la boîte en bas de l'écran
        box_x = 20
        box_y = screen_height - box_height - 20
        
        dialogue_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # Ombre de la boîte
        shadow_rect = dialogue_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=15)
        
        # Boîte de dialogue principale
        pygame.draw.rect(screen, (30, 30, 40), dialogue_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 100, 120), dialogue_rect, 3, border_radius=15)
        
        # Texte centré dans la boîte
        text_x = box_x + padding
        text_y = box_y + (box_height - text_surface.get_height()) // 2
        
        screen.blit(text_surface, (text_x, text_y))
        
        # Indicateur pour passer au dialogue suivant
        indicator_text = "Appuyez sur ESPACE pour continuer..."
        indicator_surface = pygame.font.Font(None, 16).render(indicator_text, True, (180, 180, 180))
        indicator_x = box_x + box_width - indicator_surface.get_width() - padding
        indicator_y = box_y + box_height - indicator_surface.get_height() - 10
        
        screen.blit(indicator_surface, (indicator_x, indicator_y))