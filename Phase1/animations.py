import pygame
import math


class Animation:
    """Classe de base pour toutes les animations"""

    def __init__(self, duration=1.0):
        self.elapsed_time = 0
        self.duration = duration
        self.is_finished = False

    def update(self, dt):
        """Met à jour l'animation"""
        self.elapsed_time += dt
        if self.elapsed_time >= self.duration:
            self.is_finished = True

    def draw(self, surface, position):
        """Méthode à surcharger dans les classes enfants"""
        pass

    def reset(self):
        """Réinitialise l'animation"""
        self.elapsed_time = 0
        self.is_finished = False

    def get_progress(self):
        """Retourne la progression de l'animation (0 à 1)"""
        return min(1.0, self.elapsed_time / self.duration)


class PotionMixingAnimation(Animation):
    """Animation de mélange de potion"""

    def __init__(self, duration=2.0, radius=15):
        super().__init__(duration)
        self.radius = radius
        self.bubble_colors = [
            (100, 100, 200),  # Bleu
            (200, 100, 200),  # Violet
            (200, 100, 100),  # Rouge
            (100, 200, 100)  # Vert
        ]

    def update(self, dt):
        super().update(dt)
        # Vous pourriez ajouter ici une logique spécifique à cette animation

    def draw(self, surface, position):
        """Dessine l'animation de mélange de potion"""
        center_x, center_y = position
        progress = self.get_progress()

        # Variation du rayon en fonction du temps
        current_radius = self.radius + int(math.sin(self.elapsed_time * 10) * 3)

        # Dessiner plusieurs bulles tournant autour du centre
        for i in range(8):
            angle = (self.elapsed_time * 200) + (i * 45)
            x = center_x + int(math.cos(math.radians(angle)) * current_radius)
            y = center_y + int(math.sin(math.radians(angle)) * current_radius)

            # Taille et couleur des bulles variant avec le temps
            bubble_size = 5 + int(math.sin(self.elapsed_time * 5 + i) * 2)
            color_index = (i + int(self.elapsed_time * 3)) % len(self.bubble_colors)
            bubble_color = self.bubble_colors[color_index]

            pygame.draw.circle(surface, bubble_color, (x, y), bubble_size)

        # Afficher la progression (optionnel)
        if progress < 1.0:
            progress_percent = int(progress * 100)
            font = pygame.font.SysFont('Arial', 12)
            text_surface = font.render(f"{progress_percent}%", True, (255, 255, 255))
            surface.blit(
                text_surface,
                (center_x - text_surface.get_width() // 2, center_y - 20)
            )


class AnimationManager:
    """Gestionnaire central pour toutes les animations du jeu"""

    def __init__(self):
        self.animations = {}

    def add_animation(self, name, animation, position):
        """Ajoute une animation au gestionnaire"""
        self.animations[name] = {
            "animation": animation,
            "position": position
        }

    def remove_animation(self, name):
        """Supprime une animation du gestionnaire"""
        if name in self.animations:
            del self.animations[name]

    def update(self, dt):
        """Met à jour toutes les animations actives"""
        # Créer une liste des animations à supprimer
        to_remove = []

        for name, anim_data in self.animations.items():
            animation = anim_data["animation"]
            animation.update(dt)

            # Si l'animation est terminée, la marquer pour suppression
            if animation.is_finished:
                to_remove.append(name)

        # Supprimer les animations terminées
        for name in to_remove:
            self.remove_animation(name)

    def draw(self, surface):
        """Dessine toutes les animations actives"""
        for anim_data in self.animations.values():
            animation = anim_data["animation"]
            position = anim_data["position"]
            animation.draw(surface, position)

    def is_animation_active(self, name):
        """Vérifie si une animation est active"""
        return name in self.animations