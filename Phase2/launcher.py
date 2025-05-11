import pygame
import math


class PotionProjectile(pygame.sprite.Sprite):
    """Classe représentant une potion lancée comme projectile"""

    def __init__(self, x, y, angle, power, potion):
        super().__init__()

        # Référence à la potion
        self.potion = potion

        # Chargement de l'image
        try:
            # On essaie d'utiliser l'image de la potion
            self.image = potion.image.copy()
            # Redimensionner l'image si nécessaire
            if self.image.get_width() > 20 or self.image.get_height() > 20:
                self.image = pygame.transform.scale(self.image, (20, 20))
        except (AttributeError, pygame.error):
            # Image par défaut si problème
            self.image = pygame.Surface((10, 10))
            self.image.fill((0, 255, 0))  # Vert par défaut

        self.rect = self.image.get_rect(center=(x, y))

        # Physique du projectile
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.angle = angle  # En degrés
        self.power = power  # Force du lancer (0-10)

        # Convertir l'angle en radians pour les calculs
        angle_rad = math.radians(angle)

        # Calculer les vitesses initiales
        self.velocity_x = math.cos(angle_rad) * power * 5  # Facteur 5 pour une bonne vitesse de jeu
        self.velocity_y = -math.sin(angle_rad) * power * 5  # Négatif car y augmente vers le bas

        # Gravité
        self.gravity = 9.8

        # Effet de traînée (pour l'animation)
        self.trail = []
        self.max_trail_length = 10

    def update(self, dt):
        """Mise à jour de la position du projectile"""
        # Application de la gravité
        self.velocity_y += self.gravity * dt

        # Mise à jour de la position
        self.pos_x += self.velocity_x * dt
        self.pos_y += self.velocity_y * dt

        # Mise à jour du rect
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        # Ajout à la traînée
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # Vérification si le projectile est sorti de l'écran
        if self.rect.top > 600 or self.rect.left > 800 or self.rect.right < 0:
            self.kill()

    def draw_trail(self, surface):
        """Dessine la traînée du projectile"""
        if len(self.trail) < 2:
            return

        # Dessiner une ligne entre les points de la traînée
        pygame.draw.lines(surface, (100, 100, 100), False, self.trail, 2)


class Launcher:
    """Classe pour gérer le lanceur de potions"""

    def __init__(self, x=None, y=None):
        # Position du lanceur adaptée au TMX
        if x is None:
            x = 100  # Position X du lanceur
        if y is None:
            y = 520  # Position Y du lanceur - juste au-dessus du sol dans le TMX

        self.x = x
        self.y = y

        # Paramètres du lanceur
        self.angle = 45  # Angle en degrés (0 = horizontal, 90 = vertical)
        self.power = 5  # Puissance du lancer (1-10)

        # Aspect visuel
        self.length = 50  # Longueur du lanceur
        self.color = (200, 200, 200)

        # Projectiles actifs
        self.projectiles = pygame.sprite.Group()

        # État
        self.is_aiming = False
        self.selected_potion = None

    def set_angle(self, angle):
        """Définit l'angle du lanceur"""
        self.angle = max(0, min(90, angle))

    def set_power(self, power):
        """Définit la puissance du lanceur"""
        self.power = max(1, min(10, power))

    def select_potion(self, potion):
        """Sélectionne une potion pour le lancement"""
        self.selected_potion = potion

    def launch(self):
        """Lance la potion sélectionnée"""
        if self.selected_potion is None:
            # Si pas de potion sélectionnée, lancer une pierre
            return self.launch_stone()

        # Créer un projectile à partir de la potion
        projectile = PotionProjectile(self.x, self.y, self.angle, self.power, self.selected_potion)
        self.projectiles.add(projectile)

        # Retourner la potion lancée pour que le jeu puisse la retirer de l'inventaire
        potion = self.selected_potion
        self.selected_potion = None
        return potion

    def launch_stone(self):
        """Lance une pierre (utilisé quand il n'y a plus de potions)"""
        # Créer une "fausse potion" pour représenter la pierre
        stone = type('Stone', (), {})()
        stone.effect = "dégâts légers"
        stone.power = 1
        stone.duration = 1
        stone.name = "Pierre"

        # Créer une image pour la pierre
        stone_image = pygame.Surface((8, 8))
        stone_image.fill((100, 100, 100))
        stone.image = stone_image

        # Lancer la pierre comme un projectile
        projectile = PotionProjectile(self.x, self.y, self.angle, self.power, stone)
        self.projectiles.add(projectile)

        return None  # Pas de potion à retirer de l'inventaire

    def update(self, dt):
        """Mise à jour du lanceur et des projectiles"""
        self.projectiles.update(dt)

    def draw(self, surface):
        """Dessine le lanceur et sa trajectoire prévue"""
        # Calculer les coordonnées de fin du lanceur
        end_x = self.x + math.cos(math.radians(self.angle)) * self.length
        end_y = self.y - math.sin(math.radians(self.angle)) * self.length

        # Dessiner le lanceur
        pygame.draw.line(surface, self.color, (self.x, self.y), (end_x, end_y), 5)
        pygame.draw.circle(surface, self.color, (self.x, self.y), 8)

        # Dessiner l'indicateur de puissance
        power_indicator_length = self.power * 5
        pygame.draw.line(surface, (255, 0, 0), (self.x - 25, self.y + 15),
                         (self.x - 25 + power_indicator_length, self.y + 15), 5)

        # Dessiner la trajectoire prévue si on est en train de viser
        if self.is_aiming:
            self.draw_trajectory(surface)

        # Dessiner les projectiles et leurs traînées
        for projectile in self.projectiles:
            projectile.draw_trail(surface)
        self.projectiles.draw(surface)

    def draw_trajectory(self, surface):
        """Dessine la trajectoire prévue du lancer"""
        points = []
        angle_rad = math.radians(self.angle)
        vel_x = math.cos(angle_rad) * self.power * 5
        vel_y = -math.sin(angle_rad) * self.power * 5
        pos_x, pos_y = self.x, self.y

        # Simuler la trajectoire
        for _ in range(30):  # Simuler 30 points
            pos_x += vel_x * 0.1
            pos_y += vel_y * 0.1
            vel_y += 9.8 * 0.1  # Gravité

            points.append((int(pos_x), int(pos_y)))

            # Arrêter si on sort de l'écran
            if pos_y > 600 or pos_x < 0 or pos_x > 800:
                break

        # Dessiner des points le long de la trajectoire
        for i, (x, y) in enumerate(points):
            # Réduire l'opacité au fur et à mesure
            alpha = 255 - int(i * (255 / len(points)))
            pygame.draw.circle(surface, (100, 100, 100, alpha), (x, y), 2)

    def check_collision_with_enemies(self, enemies):
        """Vérifie les collisions entre les projectiles et les ennemis"""
        hits = []

        for projectile in list(self.projectiles):
            # Vérifier si le projectile est tombé au sol
            if projectile.rect.bottom >= 550:  # Hauteur du sol
                # Si c'est une potion, elle peut avoir un effet de zone
                if hasattr(projectile.potion, 'category') and projectile.potion.category == "Zone":
                    # Effet de zone : chercher tous les ennemis à proximité
                    for enemy in enemies:
                        distance = math.sqrt((enemy.rect.centerx - projectile.rect.centerx) ** 2 +
                                             (enemy.rect.centery - projectile.rect.centery) ** 2)
                        if distance < 100:  # Rayon de l'effet
                            hits.append((enemy, projectile.potion))

                projectile.kill()
                continue

            # Collision directe avec un ennemi
            for enemy in enemies:
                if projectile.rect.colliderect(enemy.rect):
                    hits.append((enemy, projectile.potion))
                    projectile.kill()
                    break

        return hits