import pygame
import random
import math


class Enemy(pygame.sprite.Sprite):
    """Classe représentant un ennemi dans la phase de défense"""

    def __init__(self, x, y, speed=1, health=100, flying=False):
        super().__init__()

        # Type d'ennemi (pour l'instant un seul type, mais préparé pour l'extension)
        self.flying = flying

        # Chargement de l'image
        try:
            if flying:
                self.image = pygame.image.load('Assets/Art/Enemies/flying_enemy.png').convert_alpha()
            else:
                self.image = pygame.image.load('Assets/Art/Enemies/ground_enemy.png').convert_alpha()
        except FileNotFoundError:
            # Image par défaut si l'image n'existe pas
            self.image = pygame.Surface((30, 30))
            color = (255, 0, 0) if flying else (139, 69, 19)  # Rouge pour volant, marron pour terrestre
            self.image.fill(color)

        self.rect = self.image.get_rect(topleft=(x, y))

        # Attributs de l'ennemi
        self.speed = speed
        self.max_health = health
        self.health = health
        self.is_slowed = False
        self.slow_factor = 1.0  # 1.0 = vitesse normale, 0.5 = moitié de la vitesse
        self.slow_duration = 0
        self.is_burning = False
        self.burn_damage = 0
        self.burn_duration = 0
        self.is_frozen = False
        self.freeze_duration = 0

        # Attributs pour l'animation
        self.animation_frame = 0
        self.animation_speed = 0.2

        # Attributs pour le mouvement
        self.target_x = 100  # Position x cible (le laboratoire)
        self.direction = -1 if x > self.target_x else 1  # Direction vers le laboratoire

    def apply_potion_effect(self, potion):
        """Applique l'effet d'une potion à l'ennemi"""
        effect = potion.effect.lower()
        power = potion.power
        duration = potion.duration

        if "dégâts" in effect or "brûlure" in effect:
            # Effet de dégâts directs
            damage = power * 20  # 20 points de dégâts par niveau de puissance
            self.health -= damage

            # Effet de brûlure (dégâts sur la durée)
            if "brûlure" in effect:
                self.is_burning = True
                self.burn_damage = power * 5  # 5 points de dégâts par tick
                self.burn_duration = duration * 3  # 3 secondes par niveau de durée

        elif "ralenti" in effect:
            # Effet de ralentissement
            self.is_slowed = True
            self.slow_factor = 1.0 - (power * 0.2)  # Réduction de 20% de vitesse par niveau de puissance
            self.slow_duration = duration * 2  # 2 secondes par niveau de durée

        elif "esquive" in effect or "brouillard" in effect:
            # Effet de confusion (mouvement aléatoire)
            self.direction = -self.direction
            self.slow_duration = duration * 1.5

        elif "aveuglement" in effect or "cécité" in effect:
            # Effet d'aveuglement (arrêt momentané)
            self.is_frozen = True
            self.freeze_duration = duration * 1.5  # 1.5 secondes par niveau de durée

    def update(self, dt):
        """Mise à jour de l'ennemi"""
        # Gestion des effets sur la durée
        if self.is_burning:
            self.health -= self.burn_damage * dt
            self.burn_duration -= dt
            if self.burn_duration <= 0:
                self.is_burning = False

        if self.is_slowed:
            self.slow_duration -= dt
            if self.slow_duration <= 0:
                self.is_slowed = False
                self.slow_factor = 1.0

        if self.is_frozen:
            self.freeze_duration -= dt
            if self.freeze_duration <= 0:
                self.is_frozen = False

        # Mouvement de l'ennemi (sauf s'il est gelé)
        if not self.is_frozen:
            effective_speed = self.speed * self.slow_factor
            self.rect.x += self.direction * effective_speed

            # Si l'ennemi vole, ajouter un mouvement vertical sinusoïdal
            if self.flying:
                self.rect.y += math.sin(pygame.time.get_ticks() * 0.001) * 2

        # Animation de base
        self.animation_frame += self.animation_speed * dt
        if self.animation_frame >= 2:
            self.animation_frame = 0

        # Vérifier si l'ennemi est mort
        if self.health <= 0:
            self.kill()

    def draw_health_bar(self, surface):
        """Dessine la barre de vie de l'ennemi"""
        bar_width = self.rect.width
        bar_height = 5

        # Position de la barre (au-dessus de l'ennemi)
        x = self.rect.x
        y = self.rect.y - 10

        # Fond de la barre (rouge)
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))

        # Partie remplie de la barre (vert)
        fill_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, fill_width, bar_height))


class EnemyManager:
    """Gestionnaire des ennemis pour la phase de défense"""

    def __init__(self, screen_width, screen_height):
        self.enemies = pygame.sprite.Group()
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Paramètres de spawn
        self.spawn_timer = 0
        self.spawn_interval = 3.0  # Intervalle en secondes entre les spawns
        self.max_enemies = 10  # Nombre maximum d'ennemis simultanés
        self.wave_size = 20  # Nombre total d'ennemis dans une vague
        self.enemies_spawned = 0  # Compteur d'ennemis générés

        # Difficulté
        self.difficulty = 1  # Niveau de difficulté (augmente avec les vagues)

    def spawn_enemy(self):
        """Génère un nouvel ennemi"""
        if len(self.enemies) >= self.max_enemies or self.enemies_spawned >= self.wave_size:
            return

        # Décider si l'ennemi vole ou est au sol
        flying = random.random() > 0.7  # 30% de chance d'avoir un ennemi volant

        # Position de départ (pour l'instant, toujours à droite de l'écran)
        x = self.screen_width + 50

        # La hauteur dépend du type d'ennemi
        if flying:
            y = random.randint(50, self.screen_height // 2 - 50)
        else:
            y = self.screen_height - 80  # Au niveau du sol

        # Paramètres de l'ennemi en fonction de la difficulté
        speed = 0.5 + (0.2 * self.difficulty)
        health = 80 + (20 * self.difficulty)

        # Créer et ajouter l'ennemi
        enemy = Enemy(x, y, speed, health, flying)
        self.enemies.add(enemy)
        self.enemies_spawned += 1

    def update(self, dt):
        """Mise à jour du gestionnaire et des ennemis"""
        # Gestion du spawn
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and self.enemies_spawned < self.wave_size:
            self.spawn_enemy()
            self.spawn_timer = 0

        # Mise à jour des ennemis
        self.enemies.update(dt)

    def draw(self, surface):
        """Dessine tous les ennemis"""
        for enemy in self.enemies:
            surface.blit(enemy.image, enemy.rect)
            enemy.draw_health_bar(surface)

    def is_wave_complete(self):
        """Vérifie si la vague d'ennemis est terminée"""
        return self.enemies_spawned >= self.wave_size and len(self.enemies) == 0

    def reset_for_new_wave(self):
        """Réinitialise le gestionnaire pour une nouvelle vague"""
        self.enemies_spawned = 0
        self.spawn_timer = 0
        self.difficulty += 0.5  # Augmentation de la difficulté
        self.spawn_interval *= 0.9  # Réduction de l'intervalle de spawn
        if self.spawn_interval < 0.5:
            self.spawn_interval = 0.5  # Limite minimale

        # Augmentation du nombre d'ennemis par vague
        self.wave_size = int(self.wave_size * 1.2)
        if self.wave_size > 50:
            self.wave_size = 50  # Limite maximale

    def check_enemy_reached_lab(self):
        """Vérifie si un ennemi a atteint le laboratoire et retourne le nombre d'ennemis qui l'ont atteint"""
        count = 0
        for enemy in list(self.enemies):
            if enemy.rect.x <= 0:
                enemy.kill()
                count += 1
        return count