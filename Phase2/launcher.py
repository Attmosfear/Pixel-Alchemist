import pygame
import math


class PotionProjectile(pygame.sprite.Sprite):
    """Classe représentant une potion lancée comme projectile"""

    def __init__(self, x, y, angle, power, potion, floor_level=320):
        super().__init__()
        # Référence à la potion
        self.potion = potion
        self.floor_level = floor_level

        # Déterminer si c'est une pierre ou une potion
        self.is_stone = potion.name == "Pierre"

        # Chargement de l'image
        try:
            self.image = potion.image.copy()
            if self.image.get_width() > 20 or self.image.get_height() > 20:
                size = 15 if self.is_stone else 20
                self.image = pygame.transform.scale(self.image, (size, size))
        except (AttributeError, pygame.error):
            size = 8 if self.is_stone else 10
            self.image = pygame.Surface((size, size))
            color = (100, 100, 100) if self.is_stone else (0, 255, 0)
            self.image.fill(color)

        self.rect = self.image.get_rect(center=(x, y))

        # Physique du projectile
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.angle = angle

        # Convertir l'angle en radians pour les calculs
        angle_rad = math.radians(angle)

        # Calculer les vitesses initiales
        velocity_factor = 5
        if self.is_stone:
            velocity_factor = 12.5  # Pierres plus rapides

        self.velocity_x = math.cos(angle_rad) * power * velocity_factor
        self.velocity_y = -math.sin(angle_rad) * power * velocity_factor

        # Gravité
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
        if self.rect.top > self.floor_level or self.rect.left > 800 or self.rect.right < 0:
            self.kill()

    def draw_trail(self, surface):
        """Dessine la traînée du projectile"""
        if len(self.trail) < 2:
            return

        # Couleur selon le type de projectile
        if self.is_stone:
            color = (120, 120, 120)
            width = 1
        else:
            color = (100, 200, 100)
            width = 2

        # Dessiner une ligne entre les points de la traînée
        pygame.draw.lines(surface, color, False, self.trail, width)


class Launcher:
    """Classe pour gérer le lanceur de potions"""

    def __init__(self, x=100, y=300, floor_level=320):
        self.x = x
        self.y = y
        self.floor_level = floor_level

        # Paramètres du lanceur
        self.angle = 45
        self.power = 5

        # Aspect visuel
        self.length = 40
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

        # Lancer depuis l'extrémité du lanceur
        launch_x, launch_y = self.get_end_position()

        # Créer un projectile
        projectile = PotionProjectile(launch_x, launch_y, self.angle, self.power, self.selected_potion,
                                      self.floor_level)
        self.projectiles.add(projectile)

        # Retourner la potion lancée pour la retirer de l'inventaire
        potion = self.selected_potion
        self.selected_potion = None
        self.is_aiming = False
        return potion

    def launch_stone(self):
        """Lance une pierre (utilisé quand il n'y a plus de potions)"""
        # Créer une "fausse potion" pour représenter la pierre
        stone = type('Stone', (), {})()
        stone.effect = "dégâts légers"
        stone.power = 3
        stone.duration = 1
        stone.name = "Pierre"
        stone.category = "Attaque"

        # Créer une image pour la pierre
        stone_image = pygame.Surface((8, 8))
        stone_image.fill((100, 100, 100))
        stone.image = stone_image

        # Lancer depuis l'extrémité du lanceur
        launch_x, launch_y = self.get_end_position()

        # Créer le projectile
        projectile = PotionProjectile(launch_x, launch_y, self.angle, self.power, stone, self.floor_level)
        self.projectiles.add(projectile)

        self.is_aiming = False
        return None

    def handle_mouse_events(self, event):
        """Gère les événements de souris pour le launcher"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                if self.is_aiming:
                    return self.launch()
                else:
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

                # Calculer l'angle
                angle = math.atan2(dy, dx)
                angle_deg = math.degrees(angle)

                # Limiter l'angle entre 0 et 90 degrés
                self.set_angle(max(0, min(90, angle_deg)))

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
        power_color = (255, int(255 * (1 - self.power / 10)), 0)
        power_indicator_length = self.power * 5
        pygame.draw.line(surface, power_color, (self.x - 25, self.y + 15),
                         (self.x - 25 + power_indicator_length, self.y + 15), 5)

        # Dessiner la trajectoire si on vise
        if self.is_aiming:
            self.draw_trajectory(surface)

        # Dessiner les projectiles et leurs traînées
        for projectile in self.projectiles:
            projectile.draw_trail(surface)
        self.projectiles.draw(surface)

    def draw_trajectory(self, surface):
        """Dessine la trajectoire prévue du lancer"""
        start_x, start_y = self.get_end_position()

        points = []
        angle_rad = math.radians(self.angle)

        velocity_factor = 5
        if self.selected_potion is None:
            velocity_factor = 12.5

        vel_x = math.cos(angle_rad) * self.power * velocity_factor
        vel_y = -math.sin(angle_rad) * self.power * velocity_factor

        gravity = 25.0

        pos_x, pos_y = start_x, start_y

        dt = 0.05
        for i in range(40):
            vel_y += gravity * dt
            pos_x += vel_x * dt
            pos_y += vel_y * dt

            points.append((int(pos_x), int(pos_y)))

            if pos_y > self.floor_level or pos_x < 0 or pos_x > 800:
                break

        # Dessiner des points le long de la trajectoire
        for i, (x, y) in enumerate(points):
            alpha = 255 - int(i * (255 / len(points)))
            color = (255, 255, 255, alpha)

            point_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(point_surface, color, (2, 2), 2)
            surface.blit(point_surface, (x - 2, y - 2))

    def check_collision_with_enemies(self, enemies, effect_manager=None):
        """
        Vérifie les collisions entre les projectiles et les ennemis
        Si un effect_manager est fourni, crée aussi des effets au sol
        """
        hits = []

        for projectile in list(self.projectiles):
            # Vérifier si le projectile est tombé au sol
            if projectile.rect.bottom >= self.floor_level:
                # Créer un effet au sol si un gestionnaire d'effets est fourni
                if effect_manager is not None:
                    effect_manager.create_effect_for_potion(projectile.potion, projectile.rect.centerx,
                                                            self.floor_level)

                # Effet de zone pour certaines potions
                if hasattr(projectile.potion, 'category') and projectile.potion.category == "Zone":
                    for enemy in enemies:
                        distance = math.sqrt((enemy.rect.centerx - projectile.rect.centerx) ** 2 +
                                             (enemy.rect.centery - projectile.rect.centery) ** 2)
                        if distance < 100:
                            hits.append((enemy, projectile.potion))
                            # Marquer l'ennemi comme touché pour l'effet visuel
                            enemy.was_hit = True
                            enemy.hit_flash_time = 0.1  # Durée du flash en secondes

                projectile.kill()
                continue

                # Collision directe avec un ennemi
            for enemy in enemies:
                if projectile.rect.colliderect(enemy.rect):
                    hits.append((enemy, projectile.potion))
                    # Marquer l'ennemi comme touché pour l'effet visuel
                    enemy.was_hit = True
                    enemy.hit_flash_time = 0.1  # Durée du flash en secondes

                    # Créer un effet au point d'impact si un gestionnaire d'effets est fourni
                    if effect_manager is not None:
                        effect_manager.create_effect_for_potion(projectile.potion, projectile.rect.centerx,
                                                                    projectile.rect.centery)

                    projectile.kill()
                    break

        return hits