import math
from Allierbot.subordinate_bot import SubordinateBot

class FormationManager:
    def __init__(self, leader):
        self.leader = leader
        self.subordinates = []
        self.formation_radius = 60  # Distance du leader
        self.formation_type = 'circle'  # Type de formation
        
        # Créer 5 subordonnés en formation circulaire
        self.create_subordinates()
    
    def create_subordinates(self):
        """Crée 5 subordonnés positionnés en cercle autour du leader"""
        if not self.leader:
            return
        
        leader_pos = self.leader.get_position()
        num_subordinates = 10
        
        # Calculer les angles pour une répartition équilibrée en cercle
        angle_step = (2 * math.pi) / num_subordinates
        
        for i in range(num_subordinates):
            # Calculer l'angle pour ce subordonné
            angle = i * angle_step
            
            # Calculer la position initiale
            x = leader_pos[0] + math.cos(angle) * self.formation_radius
            y = leader_pos[1] + math.sin(angle) * self.formation_radius
            
            # Créer le subordonné
            subordinate = SubordinateBot(x, y, self.leader, angle, self.formation_radius)
            self.subordinates.append(subordinate)
    
    def update_formation(self, fireballs_group=None, group=None):
        """Met à jour la formation des subordonnés"""
        if not self.leader or not self.subordinates:
            return
        
        # Mettre à jour chaque subordonné avec la liste complète pour la séparation
        for subordinate in self.subordinates:
            subordinate.update(self.subordinates, fireballs_group, group)
    
    def adapt_to_leader_movement(self):
        """Adapte la formation aux mouvements du leader"""
        if not self.leader or not self.subordinates:
            return
        
        # Calculer la vitesse du leader pour ajuster la formation
        leader_velocity = getattr(self.leader, 'velocity_y', 0)
        
        # Si le leader bouge rapidement, resserrer la formation
        if abs(leader_velocity) > 2:
            self.formation_radius = max(40, self.formation_radius - 1)
        else:
            # Revenir à la formation normale
            self.formation_radius = min(60, self.formation_radius + 0.5)
        
        # Mettre à jour le rayon de formation pour tous les subordonnés
        for subordinate in self.subordinates:
            subordinate.formation_radius = self.formation_radius
    
    def get_subordinates(self):
        """Retourne la liste des subordonnés"""
        return self.subordinates
    
    def get_subordinates_sprites(self):
        """Retourne un groupe de sprites pour le rendu"""
        import pygame
        sprite_group = pygame.sprite.Group()
        for subordinate in self.subordinates:
            sprite_group.add(subordinate)
        return sprite_group
    
    def update(self, fireballs_group=None, group=None):
        """Met à jour le gestionnaire de formation"""
        self.adapt_to_leader_movement()
        self.update_formation(fireballs_group, group)
    
    def change_formation_type(self, formation_type):
        """Change le type de formation (pour extensions futures)"""
        self.formation_type = formation_type
        if formation_type == 'line':
            self.reorganize_line_formation()
        elif formation_type == 'wedge':
            self.reorganize_wedge_formation()
        # Par défaut, garder la formation circulaire
    
    def reorganize_line_formation(self):
        """Réorganise les subordonnés en ligne (pour extension future)"""
        if not self.subordinates:
            return
        
        spacing = 40
        start_offset = -(len(self.subordinates) - 1) * spacing / 2
        
        for i, subordinate in enumerate(self.subordinates):
            subordinate.formation_angle = math.pi / 2  # Tous vers le bas
            subordinate.formation_radius = abs(start_offset + i * spacing)
    
    def reorganize_wedge_formation(self):
        """Réorganise les subordonnés en formation en V (pour extension future)"""
        if not self.subordinates:
            return
        
        # Formation en V avec le leader à la pointe
        angles = [-math.pi/4, -math.pi/8, 0, math.pi/8, math.pi/4]
        
        for i, subordinate in enumerate(self.subordinates):
            if i < len(angles):
                subordinate.formation_angle = angles[i] + math.pi/2  # Ajuster pour orientation
                subordinate.formation_radius = 50 + (abs(angles[i]) * 30)  # Distance variable