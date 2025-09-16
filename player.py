import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x=100, y=100):
        super().__init__()
        
        # Chargement du sprite (avec fallback si l'image n'existe pas)
        try:
            self.sprite_sheet = pygame.image.load('assets/sprites/player/BIRDSPRITESHEET_Blue.png')
            self.image = self.get_image(0, 0)
        except pygame.error:
            # Fallback: créer un sprite simple si l'image n'existe pas
            self.image = pygame.Surface([32, 32])
            self.image.fill((0, 100, 200))  # Bleu
            pygame.draw.rect(self.image, (255, 255, 255), (0, 0, 32, 32), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Variables de mouvement
        self.speed = 3
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Variables pour l'animation
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10  # Frames par seconde
        
        # Directions pour l'animation
        self.facing_direction = 0  # 0=droite, 1=gauche, 2=haut, 3=bas
        
    def get_image(self, x, y):
        """Extrait une image du sprite sheet"""
        image = pygame.Surface([32, 32])
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image
    
    def handle_input(self, keys):
        """Gère les entrées clavier pour le mouvement"""
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Mouvement horizontal
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.velocity_x = -self.speed
            self.facing_direction = 1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.facing_direction = 0
        
        # Mouvement vertical
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.velocity_y = -self.speed
            self.facing_direction = 2
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity_y = self.speed
            self.facing_direction = 3
    
    def update(self, map_width, map_height):
        """Met à jour la position du joueur avec limitation de la carte"""
        # Sauvegarde de la position actuelle
        old_x = self.rect.x
        old_y = self.rect.y
        
        # Mise à jour de la position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Limitation pour ne pas sortir de la carte
        # Limite gauche
        if self.rect.x < 0:
            self.rect.x = 0
        # Limite droite
        if self.rect.x > map_width - self.rect.width:
            self.rect.x = map_width - self.rect.width
        # Limite haut
        if self.rect.y < 0:
            self.rect.y = 0
        # Limite bas
        if self.rect.y > map_height - self.rect.height:
            self.rect.y = map_height - self.rect.height
        
        # Animation si le joueur bouge
        if self.velocity_x != 0 or self.velocity_y != 0:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4  # 4 frames d'animation
    
    def get_position(self):
        """Retourne la position du joueur"""
        return (self.rect.x, self.rect.y)
    
    def set_position(self, x, y):
        """Définit la position du joueur"""
        self.rect.x = x
        self.rect.y = y