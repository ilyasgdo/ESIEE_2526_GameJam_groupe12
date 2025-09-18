import pygame

class UIManager:
    def __init__(self, screen_size):
        """Gère tout l'affichage de l'UI (HUD, dialogues, timers, barres, hotbar).

        on dessine toujours l'UI APRÈS le monde, en coordonnées écran.
        """
        self.screen_width, self.screen_height = screen_size
        self.layers_visible = {
            'hud': False,
            'dialog': False,
            'cinematic_bars': False,
        }
        # Pré-créer un overlay semi-transparent (utile pour des effets de fond)
        self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)

        self.font = pygame.font.Font(None, 28)
        self.dialog_text = ""

        # =========================
        # Compte à rebours circulaire
        # =========================
        self.countdown_active = False
        self.countdown_total = 0.0
        self.countdown_remaining = 0.0
        self.countdown_position = (0, 0)
        self.countdown_radius = 40
        self.countdown_bg_color = (0, 0, 0, 160)
        self.countdown_fg_color = (255, 200, 0)
        self._last_tick_ms = 0

        # =========================
        # Hotbar (barre d'items) en bas à gauche
        # =========================
        self.hotbar_slots_count = 4
        self.hotbar_slot_size = 64
        self.hotbar_margin = 12
        self.hotbar_padding = 8
        self.hotbar_bottom_offset = 12
        self.hotbar_left_offset = 12
        self.hotbar = []
        # Option: réduire/agrandir le rendu d'un slot précis (1.0 = normal)
        self.hotbar_slot_render_scale = {3: 0.8}

        # charger et griser une icône comme si utilisé
        # (voir méthode _load_icon_with_grey plus bas)
        trap_icon, trap_icon_grey = self._load_icon_with_grey(
            './traps/Bear_Trap.png',
            (0, 0, 32, 32),
            (self.hotbar_slot_size - 16, self.hotbar_slot_size - 16)
        )
        bomb_crop = (0, 48, 32, 15)
        bomb_icon, bomb_icon_grey = self._load_icon_with_grey(
            './traps/00 All_Rocket.png',
            bomb_crop,
            (self.hotbar_slot_size - 16, self.hotbar_slot_size - 16)
        )
        fire_icon, fire_icon_grey = self._load_icon_with_grey(
            './traps/All_Fire_Bullet_Pixel_16x16_00.png',
            (449, 200, 32, 16),
            (self.hotbar_slot_size - 16, self.hotbar_slot_size - 16)
        )
        # Slot 2 (index 1) -> Bear Trap
        # Slot 4 (index 3) -> Tsar Bomba II
        # Slot 0 (index 0) -> Fire Bullet
        # Slot 1 (index 2) -> Dragon Fire Breath
        fire_thrower_icon, fire_thrower_icon_grey = self._load_icon_with_grey(
            './assets/UI/DragonFireBreathTraps.png',
            None,
            (self.hotbar_slot_size - 16, self.hotbar_slot_size - 16)
        )

        # Construction de la hotbar
        for i in range(self.hotbar_slots_count):
            icon = None
            icon_grey = None
            if i == 0:
                icon = fire_icon
                icon_grey = fire_icon_grey
            elif i == 1:
                icon = trap_icon
                icon_grey = trap_icon_grey
            elif i == 2:
                icon = fire_thrower_icon
                icon_grey = fire_thrower_icon_grey
            elif i == 3:
                icon = bomb_icon
                icon_grey = bomb_icon_grey
            self.hotbar.append({
                'icon': icon,
                'icon_grey': icon_grey,
                'cooldown_total': 0.0,
                'cooldown_remaining': 0.0,
            })

        # =========================
        # Barre de stun (en haut de l'écran)
        # =========================
        self.stun_active = False
        self.stun_duration = 0.0
        self.stun_elapsed = 0.0
        self.stun_state = 'idle'  # idle | stunned | refilling
        self.stun_refill_duration = 1.2
        # Taille à l'écran
        self.stun_bar_width_ratio = 0.1  # 10% de la largeur d'écran
        self.stun_bar_height_px = 36     # hauteur fixe

        # On utilise une configuration manuelle de découpes (pixels dans assets/UI/07.png)
        self.stun_manual_base_rect = (0, 52, 16, 8)  # frame de base
        # frames overlay (progression de remplissage, 8 frames ici)
        self.stun_manual_overlay_rects = [
            (0, 52, 16, 8), (16, 52, 16, 8), (32, 52, 16, 8), (48, 52, 16, 8),
            (64, 52, 16, 8), (80, 52, 16, 8), (96, 52, 16, 8), (112, 52, 16, 8),
        ]
        self.stun_row_index_1based = 4
        self.stun_frame_width = 16
        self.stun_frame_height = 8
        # Chargement des images de la barre de stun
        try:
            sheet = pygame.image.load('./assets/UI/07.png').convert_alpha()
            if self.stun_manual_base_rect and self.stun_manual_overlay_rects:
                b = pygame.Rect(self.stun_manual_base_rect)
                self.stun_base_frame = sheet.subsurface(b).copy()
                self.stun_overlay_frames = []
                for r in self.stun_manual_overlay_rects:
                    rr = pygame.Rect(r)
                    self.stun_overlay_frames.append(sheet.subsurface(rr).copy())
            else:
                # Mode auto (non utilisé ici, conservé pour référence)
                row_y = (self.stun_row_index_1based - 1) * self.stun_frame_height
                num_cols = sheet.get_width() // self.stun_frame_width
                self.stun_frames = []
                for col in range(num_cols):
                    rect = pygame.Rect(col * self.stun_frame_width, row_y, self.stun_frame_width, self.stun_frame_height)
                    frame = sheet.subsurface(rect).copy()
                    self.stun_frames.append(frame)
        except Exception:
            # En cas d'erreur de chargement, on garde un fallback rectangle
            self.stun_frames = []
            self.stun_base_frame = None
            self.stun_overlay_frames = []

    def show(self, layer, payload=None):
        """Affiche une couche d'UI (ex: 'dialog')."""
        self.layers_visible[layer] = True
        if layer == 'dialog' and payload:
            self.dialog_text = payload

    def hide(self, layer):
        """Masque une couche d'UI."""
        self.layers_visible[layer] = False

    def toggle(self, layer):
        """Bascule visibilité d'une couche d'UI."""
        self.layers_visible[layer] = not self.layers_visible.get(layer, False)

    def handle_event(self, event):
        """Gestion d'événements clavier pour l'UI (ex: fermeture dialogue)."""
        if self.layers_visible['dialog'] and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.hide('dialog')

    def start_countdown(self, seconds, position):
        """Démarre un compte à rebours circulaire à l'écran.

        seconds: durée en secondes
        position: tuple écran (x, y)
        """
        self.countdown_total = max(0.01, float(seconds))
        self.countdown_remaining = self.countdown_total
        self.countdown_position = position
        self.countdown_active = True
        self._last_tick_ms = pygame.time.get_ticks()

    def cancel_countdown(self):
        """Annule le compte à rebours en cours."""
        self.countdown_active = False

    def update(self):
        """Met à jour les animations/chronos UI indépendantes du jeu."""
        # Compte à rebours
        if self.countdown_active:
            now = pygame.time.get_ticks()
            dt = (now - self._last_tick_ms) / 1000.0
            self._last_tick_ms = now
            self.countdown_remaining -= dt
            if self.countdown_remaining <= 0:
                self.countdown_active = False
        # Cooldowns de hotbar
        now_ms = pygame.time.get_ticks()
        if self._last_tick_ms == 0:
            self._last_tick_ms = now_ms
        dt_slots = (now_ms - self._last_tick_ms) / 1000.0
        self._last_tick_ms = now_ms
        for slot in self.hotbar:
            if slot['cooldown_remaining'] > 0:
                slot['cooldown_remaining'] -= dt_slots
                if slot['cooldown_remaining'] < 0:
                    slot['cooldown_remaining'] = 0
        # Machine à états de la barre de stun
        if self.stun_active:
            if self.stun_state == 'stunned':
                self.stun_elapsed += dt_slots
                if self.stun_elapsed >= self.stun_duration:
                    # passer à la phase de remplissage
                    self.stun_state = 'refilling'
                    self.stun_elapsed = 0.0
            elif self.stun_state == 'refilling':
                self.stun_elapsed += dt_slots
                if self.stun_elapsed >= self.stun_refill_duration:
                    # retour à plein et fin
                    self.stun_state = 'idle'
                    self.stun_active = False

    def render(self, screen):
        """Dessine toutes les couches d'UI. À appeler après le rendu du monde."""
        if self.layers_visible['cinematic_bars']:
            bar_h = int(self.screen_height * 0.12)
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, self.screen_width, bar_h))
            pygame.draw.rect(screen, (0, 0, 0), (0, self.screen_height - bar_h, self.screen_width, bar_h))

        # HUD par défaut retiré (exemple minimal)

        if self.layers_visible['dialog']:
            self.overlay.fill((0, 0, 0, 160))
            screen.blit(self.overlay, (0, 0))
            box_h = 120
            pygame.draw.rect(screen, (24, 24, 24), (40, self.screen_height - box_h - 40, self.screen_width - 80, box_h), border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), (40, self.screen_height - box_h - 40, self.screen_width - 80, box_h), 2, border_radius=10)
            text = self.font.render(self.dialog_text, True, (255, 255, 255))
            screen.blit(text, (60, self.screen_height - box_h - 20))

        # Timer circulaire
        if self.countdown_active:
            self._render_countdown(screen)

        # Hotbar
        self._render_hotbar(screen)

        # Barre de stun
        self._render_stun_bar(screen)

    def _render_countdown(self, screen):
        """Dessin du compte à rebours circulaire (fond + portion + texte)."""
        cx, cy = self.countdown_position
        r = self.countdown_radius
        pygame.draw.circle(screen, (0, 0, 0), (int(cx), int(cy)), r)
        pygame.draw.circle(screen, (220, 220, 220), (int(cx), int(cy)), r, width=2)
        ratio = max(0.0, min(1.0, self.countdown_remaining / self.countdown_total if self.countdown_total > 0 else 0))
        if ratio > 0:
            self._draw_filled_sector(screen, (cx, cy), r - 3, -90, -90 + 360 * ratio, self.countdown_fg_color)
        seconds_left = max(0, int(self.countdown_remaining + 0.999))
        label = self.font.render(str(seconds_left), True, (255, 255, 255))
        rect = label.get_rect(center=(cx, cy))
        screen.blit(label, rect)

    def _draw_filled_sector(self, screen, center, radius, start_angle_deg, end_angle_deg, color):
        """Dessine un secteur circulaire en polygone (approximation)."""
        import math
        cx, cy = center
        if end_angle_deg < start_angle_deg:
            start_angle_deg, end_angle_deg = end_angle_deg, start_angle_deg
        sweep = max(0.0, end_angle_deg - start_angle_deg)
        segments = max(6, int(sweep / 12))
        points = [(cx, cy)]
        for i in range(segments + 1):
            a = math.radians(start_angle_deg + sweep * (i / segments))
            x = cx + radius * math.cos(a)
            y = cy + radius * math.sin(a)
            points.append((x, y))
        pygame.draw.polygon(screen, color, points)

    def _render_hotbar(self, screen):
        """Dessine la hotbar (cadre, slots, icônes, timers de cooldown)."""
        total_w = self.hotbar_slots_count * self.hotbar_slot_size + (self.hotbar_slots_count - 1) * self.hotbar_padding
        total_h = self.hotbar_slot_size
        x0 = self.hotbar_left_offset
        y0 = self.screen_height - self.hotbar_bottom_offset - total_h
        pygame.draw.rect(screen, (0, 0, 0, 160), (x0 - 6, y0 - 6, total_w + 12, total_h + 12), border_radius=10)
        pygame.draw.rect(screen, (220, 220, 220), (x0 - 6, y0 - 6, total_w + 12, total_h + 12), width=2, border_radius=10)
        for i in range(self.hotbar_slots_count):
            sx = x0 + i * (self.hotbar_slot_size + self.hotbar_padding)
            sy = y0
            rect = pygame.Rect(sx, sy, self.hotbar_slot_size, self.hotbar_slot_size)
            pygame.draw.rect(screen, (30, 30, 30), rect, border_radius=8)
            pygame.draw.rect(screen, (180, 180, 180), rect, width=2, border_radius=8)
            icon = self.hotbar[i]['icon']
            icon_grey = self.hotbar[i]['icon_grey']
            cooldown_total = self.hotbar[i]['cooldown_total']
            cooldown_remaining = self.hotbar[i]['cooldown_remaining']
            if icon is not None:
                # Appliquer un scale de rendu par slot si configuré
                scale = self.hotbar_slot_render_scale.get(i, 1.0)
                if scale != 1.0:
                    w = max(1, int((self.hotbar_slot_size - 16) * scale))
                    h = max(1, int((self.hotbar_slot_size - 16) * scale))
                    icon_scaled = pygame.transform.smoothscale(icon, (w, h))
                    icon_grey_scaled = pygame.transform.smoothscale(icon_grey, (w, h)) if icon_grey is not None else None
                    target_rect = icon_scaled.get_rect(center=rect.center)
                else:
                    icon_scaled = icon
                    icon_grey_scaled = icon_grey
                    target_rect = icon.get_rect(center=rect.center)
                if cooldown_remaining > 0:
                    if icon_grey_scaled is not None:
                        screen.blit(icon_grey_scaled, target_rect)
                    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    s.fill((60, 60, 60, 120))
                    screen.blit(s, rect.topleft)
                else:
                    screen.blit(icon_scaled, target_rect)
            # Timer circulaire au-dessus du slot quand en cooldown
            if cooldown_remaining > 0 and cooldown_total > 0:
                cx = rect.centerx
                cy = rect.top - 18
                radius = 14
                ratio = cooldown_remaining / cooldown_total
                pygame.draw.circle(screen, (0, 0, 0), (cx, cy), radius)
                pygame.draw.circle(screen, (220, 220, 220), (cx, cy), radius, width=2)
                self._draw_filled_sector(screen, (cx, cy), radius - 2, -90, -90 + 360 * ratio, (255, 200, 0))
                seconds_left = max(0, int(cooldown_remaining + 0.999))
                label = self.font.render(str(seconds_left), True, (255, 255, 255))
                lrect = label.get_rect(center=(cx, cy))
                screen.blit(label, lrect)

    def activate_hotbar_slot(self, index, seconds):
        """Démarre le cooldown d'un slot de hotbar (grise l'icône et affiche un timer)."""
        if index < 0 or index >= self.hotbar_slots_count:
            return
        slot = self.hotbar[index]
        if slot['cooldown_remaining'] <= 0:
            slot['cooldown_total'] = float(seconds)
            slot['cooldown_remaining'] = float(seconds)

    def start_stun(self, seconds):
        """Déclenche un étourdissement: barre vide (shake), puis remplissage animé."""
        self.stun_duration = max(0.01, float(seconds))
        self.stun_elapsed = 0.0
        self.stun_active = True
        self.stun_state = 'stunned'

    def _render_stun_bar(self, screen):
        """Dessine la barre de stun en haut, toujours visible (base + overlay)."""
        margin_top = 8
        if getattr(self, 'stun_base_frame', None) is not None or getattr(self, 'stun_frames', []):
            target_w = int(self.screen_width * self.stun_bar_width_ratio)
            target_h = int(self.stun_bar_height_px)
            x = (self.screen_width - target_w) // 2
            y = margin_top
            if self.stun_state == 'stunned':
                import random
                x += random.randint(-2, 2)
                y += random.randint(-1, 1)
            if getattr(self, 'stun_base_frame', None) is not None:
                base_frame = self.stun_base_frame
                overlay_frames = self.stun_overlay_frames
            else:
                base_frame = self.stun_frames[0]
                overlay_frames = self.stun_frames[1:] if len(self.stun_frames) > 1 else []
            base_scaled = pygame.transform.scale(base_frame, (target_w, target_h))
            screen.blit(base_scaled, (x, y))
            if overlay_frames:
                if self.stun_state == 'stunned':
                    progress = 0.0
                elif self.stun_state == 'refilling':
                    progress = min(1.0, max(0.0, self.stun_elapsed / self.stun_refill_duration))
                else:
                    progress = 1.0
                idx = int(progress * (len(overlay_frames) - 1)) if len(overlay_frames) > 1 else 0
                overlay = overlay_frames[idx]
                overlay_scaled = pygame.transform.scale(overlay, (target_w, target_h))
                screen.blit(overlay_scaled, (x, y))
        else:
            # Fallback: simple rectangle jaune
            bar_w = int(self.screen_width * self.stun_bar_width_ratio)
            bar_h = self.stun_bar_height_px
            x = (self.screen_width - bar_w) // 2
            y = 8
            pygame.draw.rect(screen, (30, 30, 30), (x, y, bar_w, bar_h), border_radius=8)
            pygame.draw.rect(screen, (200, 200, 200), (x, y, bar_w, bar_h), width=2, border_radius=8)
            if self.stun_state == 'stunned':
                fill_ratio = 0.0
            elif self.stun_state == 'refilling':
                fill_ratio = min(1.0, max(0.0, self.stun_elapsed / self.stun_refill_duration))
            else:
                fill_ratio = 1.0
            pygame.draw.rect(screen, (255, 220, 40), (x+2, y+2, int((bar_w-4) * fill_ratio), bar_h-4), border_radius=6)

    def configure_stun_manual_slices(self, base_rect, overlay_rects):
        """Configure la barre de stun avec des découpes manuelles (pixels).

        base_rect: tuple (x, y, w, h) de la frame de base
        overlay_rects: liste de tuples (x, y, w, h) pour les frames d'overlay
        """
        try:
            sheet = pygame.image.load('./assets/UI/07.png').convert_alpha()
            b = pygame.Rect(base_rect)
            self.stun_base_frame = sheet.subsurface(b).copy()
            self.stun_overlay_frames = []
            for r in overlay_rects:
                rr = pygame.Rect(r)
                self.stun_overlay_frames.append(sheet.subsurface(rr).copy())
        except Exception:
            # En cas d'erreur, repasser en mode auto (fallback)
            self.stun_base_frame = None
            self.stun_overlay_frames = []

    def _load_icon_with_grey(self, image_path, crop_rect, target_size):
        """Charge une image, optionnellement la découpe, la redimensionne et crée une version grisée.

        image_path: chemin vers l'image
        crop_rect: None ou (x, y, w, h)
        target_size: (width, height) en pixels
        """
        try:
            sheet = pygame.image.load(image_path).convert_alpha()
            if crop_rect is not None:
                x, y, w, h = crop_rect
                src = sheet.subsurface(pygame.Rect(x, y, w, h)).copy()
            else:
                src = sheet
            icon = pygame.transform.smoothscale(src, target_size)
            icon_grey = icon.copy()
            icon_grey.fill((140, 140, 140, 255), special_flags=pygame.BLEND_RGBA_MULT)
            return icon, icon_grey
        except Exception:
            # Placeholder visuel en cas de problème de chargement
            surf = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.rect(surf, (180, 180, 180), surf.get_rect(), border_radius=6)
            grey = surf.copy()
            grey.fill((140, 140, 140, 255), special_flags=pygame.BLEND_RGBA_MULT)
            return surf, grey