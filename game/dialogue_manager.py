import pygame
import json
import os

CHARACTER_SPRITE_MAP = {
    "Héro": "Hero",
    "Terreur du Crous": "BigBoss",
    "Brigand": "Brigand",
}

class DialogueManager:
    def __init__(self, sprite_folder="assets/sprites/player", font_path=None, line_font_size=28, character_font_size=36):
        # Police pour le texte
        self.font = pygame.font.Font(font_path, line_font_size)
        self.character_font = pygame.font.Font(font_path, character_font_size)

        self.dialogues = {}
        self.active_scene = None
        self.current_line = 0
        self.active = False

        # Chargement des sprites
        self.sprites = {}
        self.sprite_folder = sprite_folder
        self.load_sprites()
        
        # Système de sons pour les dialogues longs
        self.dialogue_sounds = []
        self.current_sound_index = 0
        self.load_dialogue_sounds()

    def load_dialogue_sounds(self):
        """Charge les sons 1.mp3 à 5.mp3 pour les dialogues longs"""
        sound_folder = "assets/musics"
        for i in range(1, 6):  # 1 à 5
            sound_path = os.path.join(sound_folder, f"{i}.mp3")
            if os.path.exists(sound_path):
                try:
                    sound = pygame.mixer.Sound(sound_path)
                    self.dialogue_sounds.append(sound)
                    print(f"[DialogueManager] ✅ Son chargé: {sound_path}")
                except Exception as e:
                    print(f"[DialogueManager] ❌ Erreur chargement son {sound_path}: {e}")
            else:
                print(f"[DialogueManager] ⚠️ Son introuvable: {sound_path}")
        
        if not self.dialogue_sounds:
            print("[DialogueManager] ⚠️ Aucun son de dialogue chargé")

    def load_sprites(self):
        """Charge les sprites pour les personnages (nom du fichier = nom du personnage en minuscule)."""
        if not os.path.exists(self.sprite_folder):
            print(f"[DialogueManager] ❌ Dossier sprites introuvable : {self.sprite_folder}")
            return

        for filename in os.listdir(self.sprite_folder):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                name = os.path.splitext(filename)[0]  # garde le nom exact du fichier
                path = os.path.join(self.sprite_folder, filename)
                try:
                    self.sprites[name] = pygame.image.load(path).convert_alpha()
                except Exception as e:
                    print(f"[DialogueManager] ⚠️ Erreur chargement sprite {filename}: {e}")

        if not self.sprites:
            print("[DialogueManager] ⚠️ Aucun sprite trouvé dans le dossier.")

    def is_active(self):
        return self.active 

    def load_from_file(self, filename):
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                self.dialogues.update(json.load(f))

    def start_scene(self, scene_id):
        """Lance une séquence scénarisée (ex: 'scene_intro')"""
        if scene_id in self.dialogues:
            self.active_scene = scene_id
            self.current_line = 0
            self.active = True
            self.current_sound_index = 0  # Réinitialiser l'index des sons
        else:
            print(f"[DialogueManager] ❌ Aucune scène trouvée pour {scene_id}")

    def count_words(self, text):
        """Compte le nombre de mots dans un texte"""
        return len(text.split())

    def stop_all_sounds(self):
        """Arrête tous les sons en cours de lecture"""
        pygame.mixer.stop()
        print("[DialogueManager] 🔇 Tous les sons arrêtés")

    def play_dialogue_sound(self, text):
        """Joue un son si le texte fait plus de 5 mots"""
        if self.count_words(text) > 5 and self.dialogue_sounds:
            # Arrêter tous les sons en cours avant de jouer le nouveau
            self.stop_all_sounds()
            
            # Jouer le son suivant dans la séquence
            sound = self.dialogue_sounds[self.current_sound_index]
            sound.play()
            print(f"[DialogueManager] 🔊 Son joué: {self.current_sound_index + 1}.mp3")
            
            # Passer au son suivant (cycle de 1 à 5)
            self.current_sound_index = (self.current_sound_index + 1) % len(self.dialogue_sounds)

    def next_line(self):
        if not self.active:
            return
        
        # Arrêter tous les sons en cours lors du skip
        self.stop_all_sounds()
        
        self.current_line += 1
        if self.current_line >= len(self.dialogues[self.active_scene]):
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

        dialogue_entry = self.dialogues[self.active_scene][self.current_line]
        character = dialogue_entry.get("character", "???")
        line = dialogue_entry.get("line", "")

        # Jouer un son pour la ligne actuelle si elle est longue (seulement au début)
        if not hasattr(self, '_current_line_played') or self._current_line_played != self.current_line:
            self.play_dialogue_sound(line)
            self._current_line_played = self.current_line

        screen_width, screen_height = screen.get_size()
        
        # Zone de dialogue
        padding = 25
        box_height = 200
        box_width = screen_width - 40
        text_area_width = box_width - 2 * padding
        
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

        # --- Affichage du sprite du personnage ---
        if not character == "Narrator":
            sprite_key = CHARACTER_SPRITE_MAP.get(character, character)
            sprite_sheet = self.sprites.get(sprite_key)
            
            if sprite_sheet:
                # Découpage de la première frame (ex: 16x16 ou 32x32 selon ton sheet)
                FRAME_WIDTH, FRAME_HEIGHT = 32, 32  # ⚠️ adapte à la taille de tes sprites
                rect = pygame.Rect(0, 0, FRAME_WIDTH, FRAME_HEIGHT)
                first_frame = sprite_sheet.subsurface(rect)

                # Agrandir le sprite (par ex x6)
                sprite = pygame.transform.scale(first_frame, (FRAME_WIDTH * 10, FRAME_HEIGHT * 10))

                # Position : centré au-dessus de la boîte de dialogue
                sprite_x = box_x + 40
                sprite_y = box_y - sprite.get_height() - 20
                screen.blit(sprite, (sprite_x, sprite_y))



        # Nom du personnage
        character_surface = self.character_font.render(character + " :", True, (255, 215, 0))
        character_x = box_x + padding
        character_y = box_y + 15
        screen.blit(character_surface, (character_x, character_y))
        
        # Texte
        wrapped_lines = self.wrap_text(line, self.font, text_area_width)
        text_x = box_x + padding
        text_y = character_y + character_surface.get_height() + 15
        
        for wrapped_line in wrapped_lines:
            line_surface = self.font.render(wrapped_line, True, (255, 255, 255))
            screen.blit(line_surface, (text_x, text_y))
            text_y += line_surface.get_height() + 5
        
        # Indicateur
        indicator_text = "Appuyez sur ESPACE pour continuer..."
        indicator_surface = pygame.font.Font(None, 22).render(indicator_text, True, (200, 200, 200))
        indicator_x = box_x + box_width - indicator_surface.get_width() - padding
        indicator_y = box_y + box_height - indicator_surface.get_height() - 12
        
        screen.blit(indicator_surface, (indicator_x, indicator_y))
