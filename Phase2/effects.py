import pygame
import math
import random
import os

# Assurez-vous que le dossier d'effets existe
os.makedirs("Assets/Art/Effects", exist_ok=True)


class Effect(pygame.sprite.Sprite):
    """Classe de base pour les effets visuels et fonctionnels des potions"""

    def __init__(self, x, y, duration=1.0):
        super().__init__()
        self.x = x
        self.y = y
        self.duration = duration
        self.elapsed_time = 0
        self.is_finished = False

        # Position et taille
        self.rect = pygame.Rect(x - 50, y - 50, 100, 100)

        # Attributs pour les effets de zone
        self.is_zone_effect = False
        self.zone_radius = 0
        self.damage_per_second = 0
        self.slow_factor = 1.0
        self.stun_duration = 0
        self.blind_duration = 0
        self.repel_force = 0

        # Animation
        self.frame = 0
        self.max_frames = 1
        self.frames = []

    def update(self, dt):
        """Met à jour l'effet"""
        self.elapsed_time += dt

        # Animation
        self.frame = min(int(self.elapsed_time / self.duration * self.max_frames), self.max_frames - 1)

        if self.elapsed_time >= self.duration:
            self.is_finished = True

    def get_progress(self):
        """Retourne la progression de l'animation (0 à 1)"""
        return min(1.0, self.elapsed_time / self.duration)

    def affect_enemy(self, enemy, dt):
        """Applique les effets aux ennemis dans la zone"""
        if not self.is_zone_effect:
            return

        # Vérifier si l'ennemi est dans la zone d'effet
        distance = math.sqrt((enemy.rect.centerx - self.x) ** 2 + (enemy.rect.centery - self.y) ** 2)
        if distance <= self.zone_radius:
            # Appliquer les dégâts
            if self.damage_per_second > 0:
                enemy.health -= self.damage_per_second * dt

            # Appliquer le ralentissement
            if self.slow_factor < 1.0:
                enemy.is_slowed = True
                enemy.slow_factor = min(enemy.slow_factor, self.slow_factor)
                enemy.slow_duration = max(enemy.slow_duration, 0.5)  # Au moins 0.5 seconde

            # Appliquer l'étourdissement
            if self.stun_duration > 0:
                enemy.is_frozen = True
                enemy.freeze_duration = max(enemy.freeze_duration, self.stun_duration)

            # Appliquer l'aveuglement
            if self.blind_duration > 0:
                # Effet d'aveuglement - l'ennemi rate sa cible
                enemy.is_blinded = True
                enemy.blind_duration = max(enemy.blind_duration, self.blind_duration)

            # Appliquer la répulsion
            if self.repel_force > 0:
                # Calculer la direction de répulsion
                dx = enemy.rect.centerx - self.x
                dy = enemy.rect.centery - self.y
                distance = max(1, math.sqrt(dx * dx + dy * dy))  # Éviter division par zéro

                # Normaliser et appliquer la force
                enemy.rect.x += (dx / distance) * self.repel_force
                enemy.rect.y += (dy / distance) * self.repel_force


class ExplosionEffect(Effect):
    """Effet d'explosion pour les potions d'attaque"""

    def __init__(self, x, y, size=50, color=(255, 100, 0), duration=0.8):
        super().__init__(x, y, duration)
        self.size = size
        self.color = color
        self.particles = []
        self.max_frames = 7

        # Paramètres d'effet
        self.is_zone_effect = True
        self.zone_radius = size * 1.5
        self.damage_per_second = 30  # Dégâts de base

        # Générer des particules pour l'explosion
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            size = random.randint(2, 6)
            lifetime = random.uniform(0.3, self.duration)
            particle = {
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'lifetime': lifetime,
                'elapsed': 0,
                'color': self.color
            }
            self.particles.append(particle)

        # Chargement des images d'explosion
        self.frames = []
        try:
            for i in range(1, 8):  # Supposant 7 images nommées explosion1.png à explosion7.png
                img = pygame.image.load(f'Assets/Art/Effects/explosion{i}.png').convert_alpha()
                self.frames.append(img)
        except FileNotFoundError:
            # Images par défaut si les fichiers n'existent pas
            self._generate_default_frames()

    def _generate_default_frames(self):
        """Génère des images d'explosion par défaut"""
        self.frames = []
        for i in range(7):  # 7 frames d'animation
            scale = 0.3 + i * 0.1  # Commence petit et grossit
            surf = pygame.Surface((int(self.size * 2 * scale), int(self.size * 2 * scale)), pygame.SRCALPHA)

            # Cercle principal qui grossit
            alpha = 255 - int(180 * (i / 6))  # Devient plus transparent
            pygame.draw.circle(surf, (*self.color, alpha),
                               (int(self.size * scale), int(self.size * scale)),
                               int(self.size * scale))

            # Éclats qui s'éloignent du centre
            for _ in range(5 + i * 3):
                angle = random.uniform(0, 2 * math.pi)
                dist = (0.5 + i * 0.1) * self.size * scale
                px = int(self.size * scale + math.cos(angle) * dist)
                py = int(self.size * scale + math.sin(angle) * dist)
                p_size = random.randint(3, 8)
                p_alpha = random.randint(100, 230)
                pygame.draw.circle(surf, (*self.color, p_alpha), (px, py), p_size)

            self.frames.append(surf)

    def update(self, dt):
        """Met à jour l'explosion"""
        super().update(dt)

        # Mettre à jour les particules
        for particle in self.particles:
            particle['elapsed'] += dt
            particle['x'] += particle['vx'] * dt * 60
            particle['y'] += particle['vy'] * dt * 60

            # Appliquer une légère gravité
            particle['vy'] += 0.1

    def draw(self, surface):
        """Dessine l'explosion"""
        # Utiliser l'image de la frame actuelle
        if self.frames and self.frame < len(self.frames):
            img = self.frames[self.frame]
            img_rect = img.get_rect(center=(self.x, self.y))
            surface.blit(img, img_rect)
        else:
            # Fallback si pas d'images disponibles
            progress = self.get_progress()
            radius = self.size * (1 - progress * 0.5)  # Réduire légèrement avec le temps
            alpha = int(255 * (1 - progress))

            # Créer une surface avec canal alpha
            explosion_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (*self.color, alpha), (radius, radius), radius)

            # Appliquer un flou (simplifié)
            blur_amount = int(radius * 0.1)
            for i in range(blur_amount):
                factor = 1 - (i / blur_amount)
                pygame.draw.circle(explosion_surface, (*self.color, int(alpha * factor)),
                                   (radius, radius), radius - i)

            surface.blit(explosion_surface, (self.x - radius, self.y - radius))

        # Dessiner les particules
        for particle in self.particles:
            # Calculer l'opacité en fonction du temps de vie
            p_alpha = 255 * (1 - particle['elapsed'] / particle['lifetime'])
            if p_alpha > 0:
                pygame.draw.circle(surface, (*particle['color'], int(p_alpha)),
                                   (int(particle['x']), int(particle['y'])), particle['size'])


class SmokeEffect(Effect):
    """Effet de fumée pour les potions de statut"""

    def __init__(self, x, y, color=(150, 150, 150), duration=3.0):
        super().__init__(x, y, duration)
        self.color = color
        self.particles = []
        self.max_frames = 10

        # Paramètres d'effet
        self.is_zone_effect = True
        self.zone_radius = 80
        self.slow_factor = 0.7  # Ralentissement
        self.blind_duration = 1.0  # Durée de l'aveuglement

        # Générer des particules de fumée
        for i in range(15):
            delay = random.uniform(0, self.duration * 0.5)
            size = random.randint(5, 15)
            lifetime = random.uniform(1.0, self.duration)
            speed = random.uniform(0.5, 2)
            particle = {
                'x': self.x + random.uniform(-10, 10),
                'y': self.y + random.uniform(-5, 5),
                'vx': random.uniform(-0.5, 0.5),
                'vy': -speed,  # Monter
                'size': size,
                'lifetime': lifetime,
                'elapsed': 0,
                'delay': delay,
                'color': self.color
            }
            self.particles.append(particle)

        # Chargement des images de fumée
        self.frames = []
        try:
            for i in range(1, 11):  # Supposant 10 images nommées smoke1.png à smoke10.png
                img = pygame.image.load(f'Assets/Art/Effects/smoke{i}.png').convert_alpha()
                self.frames.append(img)
        except FileNotFoundError:
            # Images par défaut si les fichiers n'existent pas
            self._generate_default_frames()

    def _generate_default_frames(self):
        """Génère des images de fumée par défaut"""
        self.frames = []
        base_size = 40

        for i in range(10):  # 10 frames d'animation
            size = base_size + i * 8  # La fumée s'étend
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

            # Nuage principal qui s'étend
            alpha = 180 - i * 15  # Devient plus transparent

            # Dessiner plusieurs cercles pour créer un nuage
            for _ in range(8 + i):
                cx = size + random.uniform(-size / 2, size / 2)
                cy = size + random.uniform(-size / 2, size / 2)
                r = (size / 3) * random.uniform(0.7, 1.3)
                c_alpha = min(255, alpha + random.randint(-30, 30))
                pygame.draw.circle(surf, (*self.color, c_alpha), (int(cx), int(cy)), int(r))

            self.frames.append(surf)

    def update(self, dt):
        """Met à jour la fumée"""
        super().update(dt)

        # Mettre à jour les particules
        for particle in self.particles:
            if particle['delay'] > 0:
                particle['delay'] -= dt
                continue

            particle['elapsed'] += dt
            if particle['elapsed'] < particle['lifetime']:
                particle['x'] += particle['vx'] * dt * 60
                particle['y'] += particle['vy'] * dt * 60

                # Ralentir verticalement
                particle['vy'] *= 0.98

                # Grossir légèrement
                if particle['elapsed'] < particle['lifetime'] * 0.5:
                    particle['size'] += 0.1

    def draw(self, surface):
        """Dessine la fumée"""
        # Utiliser l'image de la frame actuelle
        if self.frames and self.frame < len(self.frames):
            img = self.frames[self.frame]
            img_rect = img.get_rect(center=(self.x, self.y))
            surface.blit(img, img_rect)
        else:
            # Fallback si pas d'images disponibles
            for particle in self.particles:
                if particle['delay'] > 0 or particle['elapsed'] >= particle['lifetime']:
                    continue

                # Calculer l'opacité
                alpha = 255 * (1 - particle['elapsed'] / particle['lifetime'])

                # Dessiner la particule de fumée
                if alpha > 0:
                    smoke_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                    pygame.draw.circle(smoke_surface, (*particle['color'], int(alpha)),
                                       (particle['size'], particle['size']), particle['size'])

                    # Appliquer un flou simple
                    pygame.draw.circle(smoke_surface, (*particle['color'], int(alpha * 0.7)),
                                       (particle['size'], particle['size']), particle['size'] * 0.8)

                    surface.blit(smoke_surface,
                                 (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))


class WaterEffect(Effect):
    """Effet d'éclaboussure d'eau pour les potions à base d'eau"""

    def __init__(self, x, y, color=(0, 100, 255), duration=0.8):
        super().__init__(x, y, duration)
        self.color = color
        self.droplets = []
        self.max_frames = 8

        # Paramètres d'effet
        self.is_zone_effect = True
        self.zone_radius = 60
        self.slow_factor = 0.5  # Ralentissement important

        # Générer des gouttelettes
        for _ in range(30):
            angle = random.uniform(-math.pi * 0.8, 0)  # Vers le haut principalement
            speed = random.uniform(3, 8)
            size = random.uniform(2, 5)
            lifetime = random.uniform(0.3, 0.8)
            droplet = {
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'lifetime': lifetime,
                'elapsed': 0
            }
            self.droplets.append(droplet)

        # Chargement des images d'eau
        self.frames = []
        try:
            for i in range(1, 9):  # Supposant 8 images nommées water1.png à water8.png
                img = pygame.image.load(f'Assets/Art/Effects/water{i}.png').convert_alpha()
                self.frames.append(img)
        except FileNotFoundError:
            # Images par défaut si les fichiers n'existent pas
            self._generate_default_frames()

    def _generate_default_frames(self):
        """Génère des images d'éclaboussure d'eau par défaut"""
        self.frames = []
        size = 60

        for i in range(8):  # 8 frames d'animation
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

            # Animation d'éclaboussure
            if i < 3:  # Début: flux vers le haut
                for _ in range(10 + i * 5):
                    angle = random.uniform(-math.pi, 0)  # Vers le haut
                    dist = 10 + i * 15
                    px = size + math.cos(angle) * dist
                    py = size + math.sin(angle) * dist
                    p_size = random.randint(3, 7)
                    alpha = 200 - i * 20
                    pygame.draw.circle(surf, (*self.color, alpha), (int(px), int(py)), p_size)
            else:  # Suite: étalement et formation de flaque
                # Flaque qui se forme
                alpha = 180 - (i - 3) * 20
                flaque_size = 20 + (i - 3) * 10
                pygame.draw.ellipse(surf, (*self.color, alpha),
                                    (size - flaque_size, size + 20, flaque_size * 2, flaque_size / 2))

                # Gouttes qui retombent
                for _ in range(15 - i):
                    px = size + random.uniform(-flaque_size, flaque_size)
                    py = size + random.uniform(-40, 20)
                    p_size = random.randint(2, 5)
                    p_alpha = alpha + random.randint(-40, 40)
                    pygame.draw.circle(surf, (*self.color, p_alpha), (int(px), int(py)), p_size)

            self.frames.append(surf)

    def update(self, dt):
        """Met à jour l'éclaboussure"""
        super().update(dt)

        # Mettre à jour les gouttelettes
        for droplet in self.droplets:
            droplet['elapsed'] += dt

            if droplet['elapsed'] < droplet['lifetime']:
                droplet['x'] += droplet['vx'] * dt * 60
                droplet['y'] += droplet['vy'] * dt * 60

                # Appliquer la gravité
                droplet['vy'] += 0.2

    def draw(self, surface):
        """Dessine l'éclaboussure d'eau"""
        # Utiliser l'image de la frame actuelle
        if self.frames and self.frame < len(self.frames):
            img = self.frames[self.frame]
            img_rect = img.get_rect(center=(self.x, self.y))
            surface.blit(img, img_rect)
        else:
            # Fallback si pas d'images disponibles
            for droplet in self.droplets:
                if droplet['elapsed'] >= droplet['lifetime']:
                    continue

                # Calculer l'opacité
                alpha = 255 * (1 - droplet['elapsed'] / droplet['lifetime'])

                # Dessiner la gouttelette
                if alpha > 0:
                    pygame.draw.circle(surface, (*self.color, int(alpha)),
                                       (int(droplet['x']), int(droplet['y'])), droplet['size'])


class FirePuddleEffect(Effect):
    """Effet de flaque de feu persistante"""

    def __init__(self, x, y, color=(255, 100, 0), duration=5.0):
        super().__init__(x, y, duration)
        self.color = color
        self.particles = []
        self.max_frames = 12

        # Paramètres d'effet
        self.is_zone_effect = True
        self.zone_radius = 70
        self.damage_per_second = 20  # Dégâts modérés mais constants

        # Génération de la flaque
        self.puddle_radius = 40

        # Flammes qui s'élèvent
        for _ in range(40):
            px = self.x + random.uniform(-self.puddle_radius, self.puddle_radius)
            py = self.y + random.uniform(-self.puddle_radius / 2, self.puddle_radius / 2)

            # S'assurer que le point est dans une ellipse
            if ((px - self.x) / self.puddle_radius) ** 2 + ((py - self.y) / (self.puddle_radius / 2)) ** 2 > 1:
                continue

            lifetime = random.uniform(0.5, 1.5)  # Chaque flamme est de courte durée mais se régénère
            self.particles.append({
                'x': px,
                'y': py,
                'base_x': px,  # Position de base pour l'oscillation
                'base_y': py,
                'size': random.uniform(3, 8),
                'speed': random.uniform(0.5, 2),
                'lifetime': lifetime,
                'elapsed': random.uniform(0, lifetime),  # Départ décalé
                'color': self.color,
                'phase': random.uniform(0, math.pi * 2)  # Phase pour l'oscillation
            })

        # Chargement des images de flaque de feu
        self.frames = []
        try:
            for i in range(1, 13):  # Supposant 12 images nommées fire_puddle1.png à fire_puddle12.png
                img = pygame.image.load(f'Assets/Art/Effects/fire_puddle{i}.png').convert_alpha()
                self.frames.append(img)
        except FileNotFoundError:
            # Images par défaut si les fichiers n'existent pas
            self._generate_default_frames()

    def _generate_default_frames(self):
        """Génère des images de flaque de feu par défaut"""
        self.frames = []
        size = 100

        for i in range(12):  # Animation cyclique
            surf = pygame.Surface((size, size), pygame.SRCALPHA)

            # Flaque de base (ellipse)
            pygame.draw.ellipse(surf, (*self.color, 100), (10, size // 2, size - 20, size // 3))

            # Ajouter des flammes qui dansent
            cycle = (i % 4)  # Cycle de 4 frames
            for _ in range(20):
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(10, size // 2 - 10)
                px = size // 2 + math.cos(angle) * dist
                py = size // 2 + math.sin(angle) * dist

                # Variations de hauteur selon le cycle
                height = 5 + (cycle + random.uniform(-1, 1)) * 3

                # Dessiner une flamme (triangle)
                pygame.draw.polygon(surf, (*self.color, 180), [
                    (px - 5, py),
                    (px + 5, py),
                    (px, py - height)
                ])

            self.frames.append(surf)

    def update(self, dt):
        """Met à jour la flaque de feu"""
        super().update(dt)

        # Mise à jour des particules de flamme
        for p in self.particles:
            p['elapsed'] += dt
            if p['elapsed'] >= p['lifetime']:
                # Réinitialiser la flamme plutôt que de la supprimer
                p['elapsed'] = 0
                p['size'] = random.uniform(3, 8)
                p['speed'] = random.uniform(0.5, 2)

            # Oscillation horizontale et montée
            time = pygame.time.get_ticks() * 0.001
            p['x'] = p['base_x'] + math.sin(time * 2 + p['phase']) * 3
            p['y'] = p['base_y'] - p['speed'] * p['elapsed'] * 20

            # Réduire la taille en montant
            p['size'] *= (1 - p['elapsed'] / p['lifetime'] * 0.5)

    def draw(self, surface):
        """Dessine la flaque de feu"""
        # Animation cyclique pour la flaque persistante
        frame_idx = (self.frame % self.max_frames)

        # Utiliser l'image de la frame actuelle
        if self.frames and frame_idx < len(self.frames):
            img = self.frames[frame_idx]
            img_rect = img.get_rect(center=(self.x, self.y))
            surface.blit(img, img_rect)
        else:
            # Fallback si pas d'images disponibles
            # Dessiner la flaque
            puddle_surf = pygame.Surface((self.puddle_radius * 2, self.puddle_radius), pygame.SRCALPHA)
            pygame.draw.ellipse(puddle_surf, (*self.color, 100), (0, 0, self.puddle_radius * 2, self.puddle_radius))
            surface.blit(puddle_surf, (self.x - self.puddle_radius, self.y - self.puddle_radius // 2))

            # Dessiner les flammes
            for p in self.particles:
                if p['elapsed'] < p['lifetime']:
                    alpha = int(200 * (1 - p['elapsed'] / p['lifetime']))
                    color = (self.color[0], max(0, self.color[1] - int(p['elapsed'] / p['lifetime'] * 100)), 0, alpha)
                    pygame.draw.circle(surface, color, (int(p['x']), int(p['y'])), int(p['size']))


class MudPuddleEffect(Effect):
    """Effet de flaque de boue ralentissante"""

    def __init__(self, x, y, color=(139, 69, 19), duration=4.0):
        super().__init__(x, y, duration)
        self.color = color
        self.max_frames = 6

        # Paramètres d'effet
        self.is_zone_effect = True
        self.zone_radius = 80
        self.slow_factor = 0.3  # Ralentissement important

        # Propriétés visuelles
        self.puddle_radius = 60
        self.bubbles = []

        # Générer quelques bulles de boue
        for _ in range(10):
            self.bubbles.append({
                'x': self.x + random.uniform(-self.puddle_radius * 0.7, self.puddle_radius * 0.7),
                'y': self.y + random.uniform(-self.puddle_radius * 0.4, self.puddle_radius * 0.4),
                'size': random.uniform(3, 8),
                'pop_time': random.uniform(0.5, self.duration * 0.8),
                'popped': False
            })

        # Chargement des images de flaque de boue
        self.frames = []
        try:
            for i in range(1, 7):  # Supposant 6 images nommées mud1.png à mud6.png
                img = pygame.image.load(f'Assets/Art/Effects/mud{i}.png').convert_alpha()
                self.frames.append(img)
        except FileNotFoundError:
            # Images par défaut si les fichiers n'existent pas
            self._generate_default_frames()

    def _generate_default_frames(self):
        """Génère des images de flaque de boue par défaut"""
        self.frames = []
        size = 140

        for i in range(6):  # 6 frames d'animation
            surf = pygame.Surface((size, size // 2), pygame.SRCALPHA)

            # Flaque de base (ellipse)
            alpha = 220
            pygame.draw.ellipse(surf, (*self.color, alpha), (0, 0, size, size // 2))

            # Texture de la boue (petites taches plus sombres)
            darker_color = (max(0, self.color[0] - 40), max(0, self.color[1] - 40), max(0, self.color[2] - 40))
            for _ in range(20):
                px = random.randint(10, size - 10)
                py = random.randint(5, size // 2 - 5)
                p_size = random.randint(3, 8)
                pygame.draw.circle(surf, (*darker_color, alpha), (px, py), p_size)

            # Ajouter quelques bulles
            for j in range(3):
                if random.random() > 0.3:  # 70% de chance d'avoir une bulle
                    px = random.randint(20, size - 20)
                    py = random.randint(10, size // 2 - 10)
                    p_size = random.randint(4, 10)
                    lighter_color = (
                    min(255, self.color[0] + 20), min(255, self.color[1] + 20), min(255, self.color[2] + 20))
                    pygame.draw.circle(surf, (*lighter_color, alpha - 40), (px, py), p_size)
                    # Reflet sur la bulle
                    pygame.draw.circle(surf, (255, 255, 255, 100), (px - p_size // 3, py - p_size // 3), p_size // 3)

            self.frames.append(surf)

    def update(self, dt):
        """Met à jour la flaque de boue"""
        super().update(dt)

        # Mettre à jour les bulles
        for bubble in self.bubbles:
            if not bubble['popped'] and self.elapsed_time >= bubble['pop_time']:
                bubble['popped'] = True
                # Créer une nouvelle bulle ailleurs
                if random.random() > 0.3:  # 70% de chance de remplacer
                    bubble['x'] = self.x + random.uniform(-self.puddle_radius * 0.7, self.puddle_radius * 0.7)
                    bubble['y'] = self.y + random.uniform(-self.puddle_radius * 0.4, self.puddle_radius * 0.4)
                    bubble['size'] = random.uniform(3, 8)
                    bubble['pop_time'] = self.elapsed_time + random.uniform(0.5, 2.0)
                    bubble['popped'] = False

    def draw(self, surface):
        """Dessine la flaque de boue"""
        # Choisir la bonne frame
        frame_idx = min(self.frame, len(self.frames) - 1) if self.frames else 0

        # Utiliser l'image de la frame actuelle
        if self.frames and frame_idx < len(self.frames):
            img = self.frames[frame_idx]
            img_rect = img.get_rect(center=(self.x, self.y))
            surface.blit(img, img_rect)
        else:
            # Fallback si pas d'images disponibles
            # Dessiner la flaque elliptique
            puddle_surf = pygame.Surface((self.puddle_radius * 2, self.puddle_radius), pygame.SRCALPHA)
            pygame.draw.ellipse(puddle_surf, (*self.color, 180), (0, 0, self.puddle_radius * 2, self.puddle_radius))
            surface.blit(puddle_surf, (self.x - self.puddle_radius, self.y - self.puddle_radius // 2))

            # Dessiner les bulles
            for bubble in self.bubbles:
                if not bubble['popped']:
                    # Bulle principale
                    pygame.draw.circle(surface, (*self.color, 200),
                                       (int(bubble['x']), int(bubble['y'])),
                                       int(bubble['size']))
                    # Reflet (petit cercle blanc)
                    pygame.draw.circle(surface, (255, 255, 255, 100),
                                       (int(bubble['x'] - bubble['size'] / 3), int(bubble['y'] - bubble['size'] / 3)),
                                       int(bubble['size'] / 3))


class TornadoEffect(Effect):
    """Effet de tornade tournoyante"""

    def __init__(self, x, y, color=(200, 200, 200), duration=4.0):
        super().__init__(x, y, duration)
        self.color = color
        self.max_frames = 10

        # Paramètres d'effet
        self.is_zone_effect = True
        self.zone_radius = 60
        self.damage_per_second = 15  # Dégâts moyens
        self.repel_force = 2.0  # Force de répulsion

        # Propriétés de la tornade
        self.height = 100
        self.width = 40
        self.rotation_speed = 720  # Degrés par seconde
        self.current_angle = 0

        # Particules pour l'effet
        self.particles = []
        for _ in range(50):
            self.particles.append({
                'x': self.x + random.uniform(-self.width / 2, self.width / 2),
                'y': self.y - random.uniform(0, self.height),
                'size': random.uniform(2, 6),
                'angle': random.uniform(0, 360),
                'dist': random.uniform(5, self.width / 2),
                'speed': random.uniform(1, 3),
                'color': self.color
            })

        # Chargement des images de tornade
        self.frames = []
        try:
            for i in range(1, 11):  # Supposant 10 images nommées tornado1.png à tornado10.png
                img = pygame.image.load(f'Assets/Art/Effects/tornado{i}.png').convert_alpha()
                self.frames.append(img)
        except FileNotFoundError:
            # Images par défaut si les fichiers n'existent pas
            self._generate_default_frames()

    def _generate_default_frames(self):
        """Génère des images de tornade par défaut"""
        self.frames = []
        width, height = 80, 160

        for i in range(10):  # 10 frames pour l'animation de rotation
            surf = pygame.Surface((width, height), pygame.SRCALPHA)

            # Base plus large
            base_width = width * 0.8
            pygame.draw.ellipse(surf, (*self.color, 150), (width / 2 - base_width / 2, height - 30, base_width, 30))

            # Corps de la tornade qui tourne
            angle = i * 36  # 10 frames, 360 degrés
            points = []

            # Points du côté gauche (de bas en haut)
            for j in range(6):
                h_pct = j / 5  # 0 à 1 (bas vers haut)
                curr_width = base_width * (1 - h_pct * 0.7)  # Rétréci vers le haut

                # Décalage horizontal basé sur l'angle
                h_offset = math.sin(math.radians(angle + h_pct * 360)) * curr_width / 3

                x = width / 2 - curr_width / 2 + h_offset
                y = height - 30 - h_pct * (height - 40)
                points.append((x, y))

            # Points du côté droit (de haut en bas)
            for j in range(5, -1, -1):
                h_pct = j / 5  # 0 à 1 (bas vers haut)
                curr_width = base_width * (1 - h_pct * 0.7)  # Rétréci vers le haut

                # Décalage horizontal basé sur l'angle
                h_offset = math.sin(math.radians(angle + h_pct * 360)) * curr_width / 3

                x = width / 2 + curr_width / 2 + h_offset
                y = height - 30 - h_pct * (height - 40)
                points.append((x, y))

            # Dessiner le polygone tornade
            if len(points) > 2:
                pygame.draw.polygon(surf, (*self.color, 180), points)

                # Ajouter des débris qui tournent
                for _ in range(10):
                    h_pct = random.random()  # Position verticale
                    curr_width = base_width * (1 - h_pct * 0.7) * 0.8

                    # Décalage horizontal basé sur l'angle
                    h_offset = math.sin(math.radians(angle + h_pct * 360)) * curr_width / 2

                    x = width / 2 + h_offset + random.uniform(-curr_width / 2, curr_width / 2)
                    y = height - 30 - h_pct * (height - 40)
                    size = random.randint(2, 5)

                    pygame.draw.circle(surf, (*self.color, 220), (x, y), size)

            self.frames.append(surf)

    def update(self, dt):
        """Met à jour la tornade"""
        super().update(dt)

        # Mise à jour de l'angle de rotation
        self.current_angle += self.rotation_speed * dt
        if self.current_angle >= 360:
            self.current_angle -= 360

        # Mise à jour des particules
        for p in self.particles:
            # Faire monter les particules
            p['y'] -= p['speed'] * dt * 60

            # Quand elles atteignent le haut, les replacer en bas
            if p['y'] < self.y - self.height:
                p['y'] = self.y
                p['x'] = self.x + random.uniform(-self.width / 2, self.width / 2)
                p['dist'] = random.uniform(5, self.width / 2)
                p['size'] = random.uniform(2, 6)

            # Rotation autour de l'axe central
            p['angle'] += p['speed'] * 30 * dt
            if p['angle'] >= 360:
                p['angle'] -= 360

            # Calcul de la position sur le cercle
            radial_pct = (self.y - p['y']) / self.height  # 0 en bas, 1 en haut
            current_radius = self.width / 2 * (1 - radial_pct * 0.7)  # Rétréci vers le haut
            p['x'] = self.x + math.cos(math.radians(p['angle'])) * current_radius * random.uniform(0.7, 1.0)

    def draw(self, surface):
        """Dessine la tornade"""
        # Utiliser l'image de la frame actuelle ou en générer une en fallback
        frame_idx = int(self.current_angle / 36) % 10  # 10 frames pour 360 degrés

        if self.frames and frame_idx < len(self.frames):
            img = self.frames[frame_idx]
            img_rect = img.get_rect(midbottom=(self.x, self.y))
            surface.blit(img, img_rect)
        else:
            # Fallback: dessiner les particules
            for p in self.particles:
                alpha = 150 if p['y'] < self.y - self.height * 0.8 else 200
                pygame.draw.circle(surface, (*p['color'], alpha), (int(p['x']), int(p['y'])), int(p['size']))


class CrystalEffect(Effect):
    """Effet de cristal gelant"""

    def __init__(self, x, y, color=(200, 220, 255), duration=3.0):
        super().__init__(x, y, duration)
        self.color = color
        self.max_frames = 8

        # Paramètres d'effet
        self.is_zone_effect = True
        self.zone_radius = 40
        self.stun_duration = 2.0  # Gèle pendant 2 secondes

        # Propriétés visuelles
        self.crystal_size = 30
        self.growth_time = 0.5  # Temps pour atteindre la taille max
        self.crystal_points = []

        # Générer les points du cristal
        num_spikes = random.randint(6, 10)
        for i in range(num_spikes):
            angle = i * (360 / num_spikes)
            length = self.crystal_size * random.uniform(0.8, 1.2)
            self.crystal_points.append((angle, length))

        # Chargement des images de cristal
        self.frames = []
        try:
            for i in range(1, 9):  # Supposant 8 images nommées crystal1.png à crystal8.png
                img = pygame.image.load(f'Assets/Art/Effects/crystal{i}.png').convert_alpha()
                self.frames.append(img)
        except FileNotFoundError:
            # Images par défaut si les fichiers n'existent pas
            self._generate_default_frames()

    def _generate_default_frames(self):
        """Génère des images de cristal par défaut"""
        self.frames = []
        size = 100

        for i in range(8):  # 8 frames pour l'animation
            phase = i / 7  # 0 à 1

            if i < 4:  # Phase de croissance
                growth = phase * 2  # 0 à 1 (croissance jusqu'à frame 3)
            else:  # Phase de scintillement
                growth = 1.0

            surf = pygame.Surface((size, size), pygame.SRCALPHA)

            # Dessiner le cristal
            center = (size // 2, size // 2)
            num_spikes = 8

            for j in range(num_spikes):
                angle = j * (360 / num_spikes) + (i % 4) * 5  # Légère rotation pour scintillement
                length1 = 10 + 30 * growth  # Longueur principale
                length2 = 5 + 15 * growth  # Longueur secondaire

                # Point central
                x0, y0 = center

                # Premier point du cristal
                x1 = x0 + math.cos(math.radians(angle)) * length1
                y1 = y0 + math.sin(math.radians(angle)) * length1

                # Points secondaires (pour avoir un cristal plus large)
                angle_off = 15
                x2 = x0 + math.cos(math.radians(angle + angle_off)) * length2
                y2 = y0 + math.sin(math.radians(angle + angle_off)) * length2
                x3 = x0 + math.cos(math.radians(angle - angle_off)) * length2
                y3 = y0 + math.sin(math.radians(angle - angle_off)) * length2

                # Dessiner le triangle du cristal
                points = [(x0, y0), (x2, y2), (x1, y1), (x3, y3)]

                # Couleur avec effet de scintillement
                if i >= 4:
                    alpha = 200 + (i % 4) * 10
                    brightness = 200 + (i % 4) * 15
                    color = (min(255, brightness), min(255, brightness), 255, alpha)
                else:
                    color = (*self.color, 220)

                pygame.draw.polygon(surf, color, points)

            self.frames.append(surf)

    def update(self, dt):
        """Met à jour le cristal"""
        super().update(dt)

        # Phase de croissance
        if self.elapsed_time < self.growth_time:
            growth_pct = self.elapsed_time / self.growth_time
            self.crystal_size = 30 * growth_pct  # Croissance progressive

    def draw(self, surface):
        """Dessine le cristal"""
        # Choisir la bonne frame selon l'animation
        if self.elapsed_time < self.growth_time:
            # Phase de croissance
            frame_idx = int(self.elapsed_time / self.growth_time * 4)  # 4 premières frames
        else:
            # Phase de scintillement
            remaining_time = self.elapsed_time - self.growth_time
            frame_idx = 4 + int(remaining_time * 3) % 4  # Frames 4-7 en boucle

        frame_idx = min(frame_idx, len(self.frames) - 1) if self.frames else 0

        # Utiliser l'image de la frame actuelle
        if self.frames and frame_idx < len(self.frames):
            img = self.frames[frame_idx]
            img_rect = img.get_rect(center=(self.x, self.y))
            surface.blit(img, img_rect)
        else:
            # Fallback: dessiner un cristal polygonal
            points = []
            for angle, length in self.crystal_points:
                # Ajuster la longueur en fonction de la croissance
                if self.elapsed_time < self.growth_time:
                    current_length = length * (self.elapsed_time / self.growth_time)
                else:
                    current_length = length

                x = self.x + math.cos(math.radians(angle)) * current_length
                y = self.y + math.sin(math.radians(angle)) * current_length
                points.append((x, y))

            if len(points) > 2:
                # Effet de scintillement
                if self.elapsed_time >= self.growth_time:
                    alpha = 220 + int(math.sin(self.elapsed_time * 10) * 35)
                    intensity = 220 + int(math.sin(self.elapsed_time * 10) * 35)
                    crystal_color = (min(255, intensity), min(255, intensity), 255, alpha)
                else:
                    crystal_color = (*self.color, 220)

                pygame.draw.polygon(surface, crystal_color, points)

                # Reflet lumineux au centre
                pygame.draw.circle(surface, (255, 255, 255, 180), (int(self.x), int(self.y)),
                                   int(self.crystal_size / 5))


class EffectManager:
    """Gestionnaire des effets visuels et fonctionnels"""

    def __init__(self):
        self.effects = []

    def add_effect(self, effect):
        """Ajoute un effet au gestionnaire"""
        self.effects.append(effect)

    def create_explosion(self, x, y, size=50, color=(255, 100, 0)):
        """Crée et ajoute un effet d'explosion"""
        effect = ExplosionEffect(x, y, size, color)
        self.add_effect(effect)
        return effect

    def create_smoke(self, x, y, color=(150, 150, 150)):
        """Crée et ajoute un effet de fumée"""
        effect = SmokeEffect(x, y, color)
        self.add_effect(effect)
        return effect

    def create_water_splash(self, x, y, color=(0, 100, 255)):
        """Crée et ajoute un effet d'éclaboussure d'eau"""
        effect = WaterEffect(x, y, color)
        self.add_effect(effect)
        return effect

    def create_fire_puddle(self, x, y, color=(255, 100, 0)):
        """Crée et ajoute un effet de flaque de feu"""
        effect = FirePuddleEffect(x, y, color)
        self.add_effect(effect)
        return effect

    def create_mud_puddle(self, x, y, color=(139, 69, 19)):
        """Crée et ajoute un effet de flaque de boue"""
        effect = MudPuddleEffect(x, y, color)
        self.add_effect(effect)
        return effect

    def create_tornado(self, x, y, color=(200, 200, 200)):
        """Crée et ajoute un effet de tornade"""
        effect = TornadoEffect(x, y, color)
        self.add_effect(effect)
        return effect

    def create_crystal(self, x, y, color=(200, 220, 255)):
        """Crée et ajoute un effet de cristal"""
        effect = CrystalEffect(x, y, color)
        self.add_effect(effect)
        return effect

    def create_effect_for_potion(self, potion, x, y):
        """Crée l'effet approprié en fonction du type de potion"""
        effect_name = potion.name.lower()
        effect_description = potion.effect.lower()

        # Potions de feu et d'explosion
        if "feu" in effect_name or "lave" in effect_name or "flammes" in effect_name or "explosion" in effect_name or "brûlure" in effect_description:
            if "zone" in effect_description or "flaque" in effect_description or "persistante" in effect_description:
                return self.create_fire_puddle(x, y, (255, 100, 0))
            else:
                return self.create_explosion(x, y, 50, (255, 100, 0))

        # Potions de fumée et brouillard
        elif "fumée" in effect_name or "vapeur" in effect_name or "brume" in effect_name or "brouillard" in effect_name:
            return self.create_smoke(x, y, (220, 220, 220))

        # Potions d'eau et de boue
        elif "eau" in effect_name or "boue" in effect_name or "goutte" in effect_name or "marécage" in effect_name:
            if "boue" in effect_name or "ralentit" in effect_description or "piège" in effect_description:
                return self.create_mud_puddle(x, y, (139, 69, 19))
            else:
                return self.create_water_splash(x, y, (0, 100, 255))

        # Potions de vent et tornade
        elif "tornade" in effect_name or "brise" in effect_name or "vent" in effect_description or "tempête" in effect_name:
            return self.create_tornado(x, y, (200, 200, 200))

        # Potions de cristal et gel
        elif "cristal" in effect_name or "gèle" in effect_description or "glace" in effect_description:
            return self.create_crystal(x, y, (200, 220, 255))

        # Potions de terre et pierre
        elif "terre" in effect_name or "pierre" in effect_name or "poussière" in effect_name:
            if "poussière" in effect_name:
                return self.create_smoke(x, y, (139, 69, 19))  # Fumée brune
            else:
                return self.create_explosion(x, y, 40, (139, 69, 19))  # Explosion brune

        # Potion par défaut (explosion générique)
        else:
            return self.create_explosion(x, y, 40, (0, 255, 0))  # Explosion verte par défaut

    def update(self, dt):
        """Met à jour tous les effets"""
        # Mettre à jour et supprimer les effets terminés
        self.effects = [effect for effect in self.effects if not effect.is_finished]

        for effect in self.effects:
            effect.update(dt)

    def draw(self, surface):
        """Dessine tous les effets"""
        for effect in self.effects:
            effect.draw(surface)

    def affect_enemies(self, enemies, dt):
        """Applique les effets aux ennemis"""
        for effect in self.effects:
            for enemy in enemies:
                effect.affect_enemy(enemy, dt)