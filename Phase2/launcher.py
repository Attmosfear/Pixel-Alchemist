import pygame
import math


class PotionProjectile(pygame.sprite.Sprite):
    """Classe représentant une potion lancée comme projectile"""

    def __init__(self, x, y, angle, power, potion):
        super().__init__()

        # Référence à la potion
        self.potion = potion

        # Déterminer si c'est une pierre ou une potion
        self.is_stone = potion.name == "Pierre"

        # Chargement de l'image
        try:
            # On essaie d'utiliser l'image de la potion
            self.image = potion.image.copy()
            # Redimensionner l'image si nécessaire
            if self.image.get_width() > 20 or self.image.get_height() > 20:
                size = 15 if self.is_stone else 20
                self.image = pygame.transform.scale(self.image, (size, size))
        except (AttributeError, pygame.error):
            # Image par défaut si problème
            size = 8 if self.is_stone else 10
            self.image = pygame.Surface((size, size))
            color = (100, 100, 100) if self.is_stone else (0, 255, 0)
            self.image.fill(color)

        self.rect = self.image.get_rect(center=(x, y))

        # Physique du projectile
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.angle = angle  # En degrés
        self.power = power  # Force du lancer

        # Convertir l'angle en radians pour les calculs
        angle_rad = math.radians(angle)

        # Calculer les vitesses initiales
        velocity_factor = 5
        if self.is_stone:
            velocity_factor = 12.5  # Pierres 2.5x plus rapides

        self.velocity_x = math.cos(angle_rad) * power * velocity_factor
        self.velocity_y = -math.sin(angle_rad) * power * velocity_factor  # Négatif car y augmente vers le bas

        # Gravité - augmentée pour un effet plus réaliste
        self.gravity = 25.0

        # Effet de traînée (pour l'animation)
        self.trail = []
        self.max_trail_length = 5 if self.is_stone else 10

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

        # Vérification si le projectile est sorti de l'écran ou a touché le sol
        if self.rect.top > 550 or self.rect.left > 800 or self.rect.right < 0:
            self.kill()

    def draw_trail(self, surface):
        """Dessine la traînée du projectile"""
        if len(self.trail) < 2:
            return

        # Couleur et largeur de ligne différentes selon le type de projectile
        if self.is_stone:
            # Traînée grise plus fine pour les pierres
            color = (120, 120, 120)
            width = 1
        else:
            # Couleur selon le type de potion
            if hasattr(self.potion, 'category'):
                if self.potion.category == "Attaque":
                    color = (255, 100, 100)  # Rouge pour l'attaque
                elif self.potion.category == "Défense":
                    color = (100, 100, 255)  # Bleu pour la défense
                elif self.potion.category == "Statut":
                    color = (255, 255, 100)  # Jaune pour le statut
                else:
                    color = (100, 200, 100)  # Vert par défaut
            else:
                color = (100, 200, 100)
            width = 2

        # Dessiner une ligne entre les points de la traînée
        pygame.draw.lines(surface, color, False, self.trail, width)


class Launcher:
    """Classe pour gérer le lanceur de potions"""

    def __init__(self, x=None, y=None):
        # Position du lanceur
        if x is None:
            x = 100  # Position X du lanceur
        if y is None:
            y = 520  # Position Y du lanceur

        self.x = x
        self.y = y

        # Paramètres du lanceur
        self.angle = 45  # Angle en degrés (0 = horizontal, 90 = vertical)
        self.power = 5  # Puissance du lancer (1-10)

        # Aspect visuel
        self.length = 40  # Longueur du lanceur
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

    def get_end_position(self):
        """Retourne la position de l'extrémité du lanceur"""
        angle_rad = math.radians(self.angle)
        end_x = self.x + math.cos(angle_rad) * self.length
        end_y = self.y - math.sin(angle_rad) * self.length
        return end_x, end_y

    def launch(self):
        """Lance la potion sélectionnée"""
        if self.selected_potion is None:
            # Si pas de potion sélectionnée, lancer une pierre
            return self.launch_stone()

        # Obtenir la position à l'extrémité du lanceur
        launch_x, launch_y = self.get_end_position()

        # Créer un projectile à partir de la potion
        projectile = PotionProjectile(launch_x, launch_y, self.angle, self.power, self.selected_potion)
        self.projectiles.add(projectile)

        # Retourner la potion lancée pour que le jeu puisse la retirer de l'inventaire
        potion = self.selected_potion
        self.selected_potion = None
        self.is_aiming = False
        return potion

    def launch_stone(self):
        """Lance une pierre (utilisé quand il n'y a plus de potions)"""
        # Créer une "fausse potion" pour représenter la pierre
        stone = type('Stone', (), {})()
        stone.effect = "dégâts légers"
        stone.power = 3  # Augmenté pour que les cailloux fassent plus de dégâts
        stone.duration = 1
        stone.name = "Pierre"
        stone.category = "Attaque"  # Ajouter catégorie pour les effets

        # Créer une image pour la pierre
        stone_image = pygame.Surface((8, 8))
        stone_image.fill((100, 100, 100))
        stone.image = stone_image

        # Obtenir la position à l'extrémité du lanceur
        launch_x, launch_y = self.get_end_position()

        # Utiliser la même puissance pour la trajectoire et le lancement
        projectile = PotionProjectile(launch_x, launch_y, self.angle, self.power, stone)
        self.projectiles.add(projectile)

        self.is_aiming = False
        return None  # Pas de potion à retirer de l'inventaire

    def handle_mouse_events(self, event):
        """Gère les événements de souris pour le launcher"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                if self.is_aiming:
                    # Lancer la potion sélectionnée
                    return self.launch()
                else:
                    # Commencer à viser
                    self.is_aiming = True
                    return None
            elif event.button == 4:  # Molette vers le haut
                return "prev_potion"
            elif event.button == 5:  # Molette vers le bas
                return "next_potion"
        elif event.type == pygame.MOUSEMOTION:
            if self.is_aiming:
                # Calculer l'angle en fonction de la position de la souris
                mouse_x, mouse_y = event.pos
                dx = mouse_x - self.x
                dy = self.y - mouse_y

                # Calculer l'angle en degrés
                angle = math.atan2(dy, dx)
                angle_deg = math.degrees(angle)

                # Limiter l'angle entre 0 et 90 degrés
                angle_deg = max(0, min(90, angle_deg))

                self.set_angle(angle_deg)

                # Ajuster la puissance en fonction de la distance
                distance = math.sqrt(dx ** 2 + dy ** 2)
                self.set_power(min(10, max(1, int(distance / 50))))
        return None

    def update(self, dt):
        """Mise à jour du lanceur et des projectiles"""
        self.projectiles.update(dt)

    def draw(self, surface):
        """Dessine le lanceur et sa trajectoire prévue"""
        # Calculer les coordonnées de fin du lanceur
        end_x, end_y = self.get_end_position()

        # Dessiner le lanceur
        pygame.draw.line(surface, self.color, (self.x, self.y), (end_x, end_y), 5)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 8)

        # Dessiner l'indicateur de puissance
        power_color = (255, int(255 * (1 - self.power / 10)), 0)  # Rouge à jaune
        power_indicator_length = self.power * 5
        pygame.draw.line(surface, power_color, (self.x - 25, self.y + 15),
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
        # Obtenir le point de départ réel (extrémité du lanceur)
        start_x, start_y = self.get_end_position()

        # Utiliser exactement les mêmes valeurs que celles utilisées pour lancer le projectile
        points = []
        angle_rad = math.radians(self.angle)

        # Même facteur de vitesse que dans PotionProjectile
        velocity_factor = 5
        if self.selected_potion is None:  # C'est une pierre
            velocity_factor = 12.5

        vel_x = math.cos(angle_rad) * self.power * velocity_factor
        vel_y = -math.sin(angle_rad) * self.power * velocity_factor

        # Même gravité que dans PotionProjectile
        gravity = 25.0

        # Position initiale = extrémité du lanceur
        pos_x, pos_y = start_x, start_y

        # Simuler la trajectoire avec les mêmes paramètres
        dt = 0.05
        for i in range(40):
            # Mettre à jour selon la physique
            vel_y += gravity * dt
            pos_x += vel_x * dt
            pos_y += vel_y * dt

            points.append((int(pos_x), int(pos_y)))

            # Arrêter si on sort de l'écran ou touche le sol
            if pos_y > 550 or pos_x < 0 or pos_x > 800:
                break

        # Dessiner des points le long de la trajectoire
        for i, (x, y) in enumerate(points):
            # Réduire l'opacité au fur et à mesure
            alpha = 255 - int(i * (255 / len(points)))
            color = (255, 255, 255, alpha)

            # Créer une surface transparente pour le point
            point_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(point_surface, color, (2, 2), 2)
            surface.blit(point_surface, (x - 2, y - 2))

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