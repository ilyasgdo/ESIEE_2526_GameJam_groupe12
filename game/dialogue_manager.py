import pygame
import json
import os

class DialogueManager:
    def __init__(self, font_path=None, line_font_size=28, character_font_size=36):
        # Police pour le texte de dialogue (plus grande)
        self.font = pygame.font.Font(font_path, line_font_size)
        # Police encore plus grande pour le nom du personnage
        self.character_font = pygame.font.Font(font_path, character_font_size)

        self.dialogues = {}
        self.active_scene = None
        self.current_line = 0
        self.active = False

    def is_active(self):
        return self.active 

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
            self.active = True
        else:
            print(f"[DialogueManager] Aucune scène trouvée pour {scene_id}")

    def next_line(self):
        if not self.active:
            return
        self.current_line += 1
        if self.current_line >= len(self.dialogues[self.active_scene]):
            # Fin de la séquence
            self.active = False
            self.active_scene = None

    def wrap_text(self, text, font, max_width):
        """Découpe le texte pour qu'il rentre dans max_width"""
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return lines

    def draw(self, screen):
        if not self.active:
            return

        # Récupérer la réplique courante
        dialogue_entry = self.dialogues[self.active_scene][self.current_line]
        character = dialogue_entry.get("character", "???")
        line = dialogue_entry.get("line", "")

        # Dimensions de l'écran
        screen_width, screen_height = screen.get_size()
        
        # Taille de la boîte de dialogue
        padding = 25
        box_height = 200
        box_width = screen_width - 40
        text_area_width = box_width - 2 * padding
        
        # Position de la boîte
        box_x = 20
        box_y = screen_height - box_height - 20
        
        dialogue_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # Ombre
        shadow_rect = dialogue_rect.copy()
        shadow_rect.x += 5
        shadow_rect.y += 5
        pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=15)
        
        # Boîte principale
        pygame.draw.rect(screen, (30, 30, 40), dialogue_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 100, 120), dialogue_rect, 3, border_radius=15)
        
        # Affichage du nom du personnage
        character_surface = self.character_font.render(character + " :", True, (255, 215, 0))
        character_x = box_x + padding
        character_y = box_y + 15
        screen.blit(character_surface, (character_x, character_y))
        
        # Affichage du texte avec retour à la ligne
        wrapped_lines = self.wrap_text(line, self.font, text_area_width)
        text_x = box_x + padding
        text_y = character_y + character_surface.get_height() + 15
        
        for wrapped_line in wrapped_lines:
            line_surface = self.font.render(wrapped_line, True, (255, 255, 255))
            screen.blit(line_surface, (text_x, text_y))
            text_y += line_surface.get_height() + 5  # espacement entre lignes
        
        # Indicateur "Appuyer pour continuer"
        indicator_text = "Appuyez sur ESPACE pour continuer..."
        indicator_surface = pygame.font.Font(None, 22).render(indicator_text, True, (200, 200, 200))
        indicator_x = box_x + box_width - indicator_surface.get_width() - padding
        indicator_y = box_y + box_height - indicator_surface.get_height() - 12
        
        screen.blit(indicator_surface, (indicator_x, indicator_y))
