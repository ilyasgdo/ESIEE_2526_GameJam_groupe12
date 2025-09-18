# python
import os
import pygame


class MusicGame:
    def __init__(self, music_volume=0.6, sfx_volume=1.0, channels=16):
        # Initialisation sûre du mixer
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"[Audio] Impossible d'initialiser le mixer: {e}")
        pygame.mixer.set_num_channels(channels)

        self.music_volume = float(max(0.0, min(1.0, music_volume)))
        self.sfx_volume = float(max(0.0, min(1.0, sfx_volume)))
        self._sfx_cache: dict[str, pygame.mixer.Sound] = {}
        self._music_path: str | None = None

        self._running_channel = None
        self._running_sound = None
        self._running_path = None
        self._running_is_playing = False

        pygame.mixer.music.set_volume(self.music_volume)

    # --- Musique de fond ---
    def load_music(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"[Audio] Fichier musique introuvable: {path}")
        self._music_path = path
        pygame.mixer.music.load(path)

    def play_music(self, path: str | None = None, loop: int = -1, volume: float | None = None, fade_in: int = 0):
        if path:
            self.load_music(path)
        if volume is not None:
            self.set_music_volume(volume)
        if self._music_path is None:
            raise RuntimeError("[Audio] Aucune musique chargée.")
        pygame.mixer.music.play(loops=loop, fade_ms=max(0, int(fade_in)))

    def stop_music(self, fade_out: int = 500):
        try:
            pygame.mixer.music.fadeout(max(0, int(fade_out)))
        except pygame.error:
            pygame.mixer.music.stop()

    def pause_music(self):
        pygame.mixer.music.pause()

    def resume_music(self):
        pygame.mixer.music.unpause()

    def is_music_playing(self) -> bool:
        return pygame.mixer.music.get_busy()

    def set_music_volume(self, volume: float):
        self.music_volume = float(max(0.0, min(1.0, volume)))
        pygame.mixer.music.set_volume(self.music_volume)

    # --- Effets sonores ---
    def preload_sfx(self, name: str, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"[Audio] Fichier SFX introuvable: {path}")
        snd = pygame.mixer.Sound(path)
        snd.set_volume(self.sfx_volume)
        self._sfx_cache[name] = snd

    def play_sfx(self, key_or_path: str, volume: float | None = None):
        # key dans le cache ou chemin direct
        snd = self._sfx_cache.get(key_or_path)
        if snd is None:
            path = key_or_path
            if not os.path.exists(path):
                raise FileNotFoundError(f"[Audio] SFX introuvable: {path}")
            snd = pygame.mixer.Sound(path)
        if volume is not None:
            snd.set_volume(float(max(0.0, min(1.0, volume))))
        else:
            snd.set_volume(self.sfx_volume)

        ch = pygame.mixer.find_channel(True)
        ch.play(snd)

    def set_sfx_volume(self, volume: float):
        self.sfx_volume = float(max(0.0, min(1.0, volume)))
        for snd in self._sfx_cache.values():
            snd.set_volume(self.sfx_volume)

    def start_running_sound(self, path='assets/musics/running_sound.ogg', volume=0.3, fade_in=50):
        """Lance le son de course en boucle si pas déjà en cours."""
        try:
            import os, pygame
            if self._running_is_playing:
                return
            if not os.path.exists(path):
                print(f"[Audio] Son de course introuvable: {path}")
                return
            if self._running_sound is None or self._running_path != path:
                self._running_sound = pygame.mixer.Sound(path)
                self._running_path = path
            self._running_sound.set_volume(float(max(0.0, min(1.0, volume))))
            ch = self._running_channel or pygame.mixer.find_channel(True)
            if ch is None:
                print("[Audio] Aucun canal dispo pour le son de course.")
                return
            ch.play(self._running_sound, loops=-1, fade_ms=max(0, int(fade_in)))
            self._running_channel = ch
            self._running_is_playing = True
        except Exception as e:
            print(f"[Audio] Erreur start_running_sound: {e}")

    def stop_running_sound(self, fade_out=100):
        """Arrête le son de course s'il est en cours."""
        try:
            import pygame
            if not self._running_is_playing:
                return
            ch = self._running_channel
            if ch is not None:
                try:
                    ch.fadeout(max(0, int(fade_out)))
                except pygame.error:
                    ch.stop()
            self._running_is_playing = False
        except Exception as e:
            print(f"[Audio] Erreur stop_running_sound: {e}")