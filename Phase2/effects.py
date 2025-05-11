import pygame
import math
import random


class Effect(pygame.sprite.Sprite):
    """Classe de base pour les effets visuels"""

    def __init__(self, x, y, duration=1.0):
        super().__init__()
        self.x = x
        self.y = y
        self.duration = duration
        self.elapsed_time = 0
        self.is_finished = False

    def update(self, dt):
        """Met à jour l'effet"""
        self.elapsed_time += dt
        if self.elapsed_time >= self.duration:
            self.is_finished = True

    def get_progress(self):
        """Retourne la progression de l'animation (0 à 1)"""
        return min(1.0, self.elapsed_time / self.duration)


class ExplosionEffect(Effect):
    """Effet d'explosion pour les potions d'attaque"""

    def __init__(self, x, y, size=50, color=(255, 100, 0), duration=0.5):
        super().__init__(x, y, duration)
        self.size = size
        self.color = color
        self.particles = []

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

    def update(self, dt):
        """Met à jour l'explosion"""
        super().update(dt)

        # Mettre à jour les particules
        for particle in self.particles:
            particle['elapsed'] += dt
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']

            # Appliquer une légère gravité
            particle['vy'] += 0.1

    def draw(self, surface):
        """Dessine l'explosion"""
        # Dessiner le cercle principal avec une opacité décroissante
        progress = self.get_progress()
        radius = self.size * (1 - progress)
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

    def __init__(self, x, y, color=(150, 150, 150), duration=2.0):
        super().__init__(x, y, duration)
        self.color = color
        self.particles = []

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
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']

                # Ralentir verticalement
                particle['vy'] *= 0.98

                # Grossir légèrement
                if particle['elapsed'] < particle['lifetime'] * 0.5:
                    particle['size'] += 0.1

    def draw(self, surface):
        """Dessine la fumée"""
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
        for droplet in self.droplets:
            if droplet['elapsed'] >= droplet['lifetime']:
                continue

            # Calculer l'opacité
            alpha = 255 * (1 - droplet['elapsed'] / droplet['lifetime'])

            # Dessiner la gouttelette
            if alpha > 0:
                pygame.draw.circle(surface, (*self.color, int(alpha)),
                                   (int(droplet['x']), int(droplet['y'])), droplet['size'])


class EffectManager:
    """Gestionnaire des effets visuels"""

    def __init__(self):
        self.effects = []

    def add_effect(self, effect):
        """Ajoute un effet au gestionnaire"""
        self.effects.append(effect)

    def create_explosion(self, x, y, size=50, color=(255, 100, 0)):
        """Crée et ajoute un effet d'explosion"""
        effect = ExplosionEffect(x, y, size, color)
        self.add_effect(effect)

    def create_smoke(self, x, y, color=(150, 150, 150)):
        """Crée et ajoute un effet de fumée"""
        effect = SmokeEffect(x, y, color)
        self.add_effect(effect)

    def create_water_splash(self, x, y, color=(0, 100, 255)):
        """Crée et ajoute un effet d'éclaboussure d'eau"""
        effect = WaterEffect(x, y, color)
        self.add_effect(effect)

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