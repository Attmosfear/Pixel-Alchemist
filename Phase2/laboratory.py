import pygame


class Laboratory:
    """Classe représentant le laboratoire que le joueur défend"""

    def __init__(self, x, y, width=100, height=150):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # État du laboratoire
        self.health = 100
        self.max_health = 100
        self.upgrade_level = 1

        # Chargement des images
        try:
            self.image = pygame.image.load('Assets/Art/Buildings/laboratory.png').convert_alpha()
        except FileNotFoundError:
            # Image par défaut
            self.image = pygame.Surface((width, height))
            self.image.fill((150, 150, 150))

            # Toit
            roof_coords = [(0, 0), (width, 0), (width // 2, -30)]
            pygame.draw.polygon(self.image, (200, 100, 100), roof_coords)

            # Fenêtres
            pygame.draw.rect(self.image, (100, 200, 255), (20, 30, 20, 20))
            pygame.draw.rect(self.image, (100, 200, 255), (60, 30, 20, 20))
            pygame.draw.rect(self.image, (100, 200, 255), (40, 70, 20, 20))

            # Porte
            pygame.draw.rect(self.image, (100, 70, 40), (35, 110, 30, 40))

        # Créer un rectangle pour les collisions
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        """Dessine le laboratoire"""
        # Dessiner l'image du laboratoire
        surface.blit(self.image, (self.x, self.y))

        # Dessiner la barre de vie au-dessus du laboratoire
        bar_width = self.width
        bar_height = 10

        # Fond rouge
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 20, bar_width, bar_height))

        # Partie verte proportionnelle à la santé
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (0, 255, 0), (self.x, self.y - 20, health_width, bar_height))

    def take_damage(self, amount):
        """Réduit la santé du laboratoire"""
        self.health = max(0, self.health - amount)
        return self.health <= 0  # Retourne True si le laboratoire est détruit

    def repair(self, amount):
        """Répare le laboratoire"""
        self.health = min(self.max_health, self.health + amount)

    def upgrade(self):
        """Améliore le laboratoire"""
        self.upgrade_level += 1

        # Augmenter la santé maximale de 25% à chaque amélioration
        old_max = self.max_health
        self.max_health = int(self.max_health * 1.25)

        # Restaurer une partie de la santé avec l'amélioration
        health_bonus = (self.max_health - old_max) // 2
        self.health = min(self.max_health, self.health + health_bonus)

        # Autres améliorations possibles à implémenter :
        # - Réduction des dégâts
        # - Réparation automatique
        # - Zone de protection

        return self.upgrade_level