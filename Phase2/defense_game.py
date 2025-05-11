import pygame
import pytmx
import pyscroll
import math
import random
from Phase2.enemy import EnemyManager
from Phase2.launcher import Launcher
from Phase2.laboratory import Laboratory
from Phase2.effects import EffectManager


class DefenseGame:
    """Classe principale pour la phase de défense du laboratoire"""

    def __init__(self, screen, player, potions):
        self.screen = screen
        self.player = player
        self.native_surface = pygame.Surface((800, 600))  # Plus grande pour la phase de défense

        # Récupération des potions créées dans la phase 1
        self.available_potions = list(potions)

        # Laboratoire
        self.laboratory = Laboratory(50, 400)

        # Lanceur de potions
        self.launcher = Launcher(100, 500)

        # Gestionnaire d'ennemis
        self.enemy_manager = EnemyManager(800, 600)

        # Gestionnaire d'effets visuels
        self.effect_manager = EffectManager()

        # État du jeu
        self.wave = 1
        self.score = 0

        # Interface
        self.font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 32)
        self.selected_potion_index = 0 if self.available_potions else -1

        # Gestion du temps
        self.wave_timer = 0
        self.wave_duration = 60  # Durée d'une vague en secondes

        # Charger le background TMX pour la phase de défense
        try:
            # Assurez-vous que le chemin est correct selon votre structure de dossiers
            self.tmx_data = pytmx.util_pygame.load_pygame("Assets/Map/Main 2/Main 2.tmx")
            map_data = pyscroll.data.TiledMapData(self.tmx_data)

            # Créer le renderer pour afficher la carte TMX
            self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, (800, 600))

            # Créer un groupe pour dessiner la carte
            self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=1)

            # Message de succès
            print("Background TMX chargé avec succès pour la phase de défense!")

            # Utiliser le background TMX au lieu de l'image statique
            self.use_tmx_background = True
        except Exception as e:
            # En cas d'erreur, utiliser le background par défaut
            print(f"Erreur lors du chargement du background TMX: {e}")
            print("Utilisation du background par défaut")
            self.use_tmx_background = False

            # Charger le background par défaut comme auparavant
            try:
                self.background = pygame.image.load('Assets/Art/Backgrounds/defense_bg.png').convert()
            except FileNotFoundError:
                # Image par défaut si l'image n'existe pas
                self.background = pygame.Surface((800, 600))
                self.background.fill((100, 150, 255))  # Fond bleu ciel

                # Sol
                pygame.draw.rect(self.background, (100, 70, 0), (0, 550, 800, 50))

    def handle_events(self):
        """Gère les événements clavier/souris"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                # Changer la potion sélectionnée
                elif event.key == pygame.K_LEFT:
                    if self.available_potions:
                        self.selected_potion_index = (self.selected_potion_index - 1) % len(self.available_potions)
                        self.launcher.select_potion(self.available_potions[self.selected_potion_index])

                elif event.key == pygame.K_RIGHT:
                    if self.available_potions:
                        self.selected_potion_index = (self.selected_potion_index + 1) % len(self.available_potions)
                        self.launcher.select_potion(self.available_potions[self.selected_potion_index])

                # Ajuster l'angle du lanceur
                elif event.key == pygame.K_UP:
                    self.launcher.set_angle(self.launcher.angle + 5)

                elif event.key == pygame.K_DOWN:
                    self.launcher.set_angle(self.launcher.angle - 5)

                # Ajuster la puissance
                elif event.key == pygame.K_z:
                    self.launcher.set_power(self.launcher.power + 1)

                elif event.key == pygame.K_s:
                    self.launcher.set_power(self.launcher.power - 1)

                # Lancer une potion
                elif event.key == pygame.K_SPACE:
                    self.launcher.is_aiming = not self.launcher.is_aiming

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    if self.launcher.is_aiming:
                        # Lancer la potion sélectionnée
                        used_potion = self.launcher.launch()

                        # Si une potion a été lancée, la retirer de la liste des potions disponibles
                        if used_potion is not None and used_potion in self.available_potions:
                            self.available_potions.remove(used_potion)
                            if self.available_potions:
                                self.selected_potion_index = min(self.selected_potion_index,
                                                                 len(self.available_potions) - 1)
                                self.launcher.select_potion(self.available_potions[self.selected_potion_index])
                            else:
                                self.selected_potion_index = -1
                                self.launcher.select_potion(None)

                        self.launcher.is_aiming = False

        # Vérifier si la souris est maintenue enfoncée pour viser
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] and self.launcher.is_aiming:
            # Calculer l'angle en fonction de la position de la souris
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.launcher.x
            dy = self.launcher.y - mouse_y

            # Calculer l'angle en degrés
            angle = math.atan2(dy, dx)
            angle_deg = math.degrees(angle)

            # Limiter l'angle entre 0 et 90 degrés
            angle_deg = max(0, min(90, angle_deg))

            self.launcher.set_angle(angle_deg)

        return True

    def update(self, dt):
        """Mise à jour de tous les éléments du jeu"""
        # Mise à jour du lanceur et des projectiles
        self.launcher.update(dt)

        # Mise à jour des ennemis
        self.enemy_manager.update(dt)

        # Mise à jour des effets visuels
        self.effect_manager.update(dt)

        # Vérifier les collisions entre projectiles et ennemis
        hits = self.launcher.check_collision_with_enemies(self.enemy_manager.enemies)
        for enemy, potion in hits:
            # Appliquer l'effet de la potion à l'ennemi
            enemy.apply_potion_effect(potion)

            # Créer l'effet visuel approprié
            hit_x, hit_y = enemy.rect.center

            # Déterminer le type d'effet en fonction de la potion
            if hasattr(potion, 'effect'):
                effect_name = potion.effect.lower()

                if "dégâts" in effect_name or "brûlure" in effect_name:
                    self.effect_manager.create_explosion(hit_x, hit_y, 30, (255, 100, 0))
                elif "ralenti" in effect_name or "boue" in effect_name:
                    self.effect_manager.create_smoke(hit_x, hit_y, (139, 69, 19))  # Marron
                elif "aveuglement" in effect_name or "vapeur" in effect_name:
                    self.effect_manager.create_smoke(hit_x, hit_y, (200, 200, 200))  # Gris
                elif "brouillard" in effect_name:
                    self.effect_manager.create_water_splash(hit_x, hit_y, (200, 200, 255))
                else:
                    # Effet par défaut
                    self.effect_manager.create_explosion(hit_x, hit_y, 20, (0, 255, 0))

            # Ajouter des points au score
            self.score += 10  # Points pour avoir touché un ennemi

        # Vérifier si des ennemis ont atteint le laboratoire
        enemies_reached = self.enemy_manager.check_enemy_reached_lab()
        if enemies_reached > 0:
            # Réduire la santé du laboratoire
            lab_destroyed = self.laboratory.take_damage(enemies_reached * 10)  # 10 points de dégâts par ennemi
            if lab_destroyed:
                self.game_over()

        # Vérifier la fin de la vague
        self.wave_timer += dt
        if self.enemy_manager.is_wave_complete() or self.wave_timer >= self.wave_duration:
            self.next_wave()

    def draw(self):
        """Affiche tous les éléments du jeu"""
        # Dessiner le fond
        if hasattr(self, 'use_tmx_background') and self.use_tmx_background:
            # Utiliser le background TMX
            self.group.draw(self.screen)
        else:
            # Utiliser le background statique
            self.screen.blit(self.background, (0, 0))

        # Dessiner le laboratoire (seulement si on n'utilise pas le TMX, car il est déjà dans le TMX)
        if not hasattr(self, 'use_tmx_background') or not self.use_tmx_background:
            self.laboratory.draw(self.screen)

        # Dessiner les effets visuels (derrière les ennemis)
        self.effect_manager.draw(self.screen)

        # Dessiner les ennemis
        self.enemy_manager.draw(self.screen)

        # Dessiner le lanceur et les projectiles
        self.launcher.draw(self.screen)

        # Afficher les informations de la vague et le score
        wave_text = self.font.render(f"Vague: {self.wave}", True, (255, 255, 255))
        self.screen.blit(wave_text, (220, 15))

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (220, 40))

        # Afficher le temps restant pour la vague
        time_left = max(0, self.wave_duration - self.wave_timer)
        time_text = self.font.render(f"Temps: {int(time_left)}s", True, (255, 255, 255))
        self.screen.blit(time_text, (350, 15))

        # Afficher les potions disponibles
        self.draw_available_potions()

        # Si la partie est terminée, afficher le message de fin
        if self.laboratory.health <= 0:
            self.draw_game_over()

        # Mettre à jour l'affichage
        pygame.display.flip()

    def draw_available_potions(self):
        """Affiche les potions disponibles en bas de l'écran"""
        start_x = 50
        y = 550

        # Dessiner un fond pour la sélection de potions
        pygame.draw.rect(self.screen, (50, 50, 50, 180), (0, 530, 800, 70))

        # Texte informatif
        if not self.available_potions:
            info_text = self.font.render("Plus de potions ! Utilisez les pierres (espace)", True, (255, 200, 200))
            self.screen.blit(info_text, (250, 555))
            return

        # Dessiner chaque potion
        for i, potion in enumerate(self.available_potions):
            # Cadre de sélection pour la potion active
            if i == self.selected_potion_index:
                pygame.draw.rect(self.screen, (255, 255, 0), (start_x + i * 60 - 2, y - 2, 44, 44), 2)

            # Dessiner l'image de la potion
            try:
                potion_img = potion.image
                if potion_img.get_width() > 40 or potion_img.get_height() > 40:
                    potion_img = pygame.transform.scale(potion_img, (40, 40))
                self.screen.blit(potion_img, (start_x + i * 60, y))
            except (AttributeError, pygame.error):
                # Dessiner un rectangle de couleur si pas d'image
                color = (0, 255, 0)  # Vert par défaut
                if hasattr(potion, 'category'):
                    if potion.category == "Attaque":
                        color = (255, 0, 0)  # Rouge pour l'attaque
                    elif potion.category == "Défense":
                        color = (0, 0, 255)  # Bleu pour la défense
                    elif potion.category == "Statut":
                        color = (255, 255, 0)  # Jaune pour le statut

                pygame.draw.rect(self.screen, color, (start_x + i * 60, y, 40, 40))

            # Nom de la potion en petit en dessous
            name_text = self.font.render(potion.name[:8], True, (255, 255, 255))
            self.screen.blit(name_text, (start_x + i * 60, y + 42))

        # Instructions
        instructions = self.font.render(
            "← → : Changer de potion | ↑↓ : Ajuster angle | Z/S : Puissance | Espace : Viser/Tirer", True,
            (200, 200, 200))
        self.screen.blit(instructions, (150, 510))

    def draw_game_over(self):
        """Affiche l'écran de fin de partie"""
        # Overlay semi-transparent
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Texte de game over
        game_over_text = self.title_font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(game_over_text, (400 - game_over_text.get_width() // 2, 200))

        # Score final
        score_text = self.font.render(f"Score final: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (400 - score_text.get_width() // 2, 250))

        # Vagues survécues
        wave_text = self.font.render(f"Vagues survécues: {self.wave - 1}", True, (255, 255, 255))
        self.screen.blit(wave_text, (400 - wave_text.get_width() // 2, 280))

        # Instructions pour continuer
        continue_text = self.font.render("Appuyez sur ECHAP pour revenir à la phase de préparation", True,
                                         (200, 200, 200))
        self.screen.blit(continue_text, (400 - continue_text.get_width() // 2, 350))

    def next_wave(self):
        """Passe à la vague suivante"""
        self.wave += 1
        self.wave_timer = 0

        # Augmenter légèrement la durée de la vague
        self.wave_duration = min(120, self.wave_duration + 5)  # Max 2 minutes

        # Réinitialiser l'enemy manager pour la nouvelle vague
        self.enemy_manager.reset_for_new_wave()

        # Donner quelques points bonus pour avoir survécu à la vague
        self.score += 100 * (self.wave - 1)

        # Petite régénération de santé entre les vagues
        self.laboratory.repair(20)

    def game_over(self):
        """Gère la fin de partie"""
        # Les points bonus seront déjà comptabilisés dans le score

        # Sauvegarder les données dans le profil du joueur
        self.player.score += self.score
        self.player.gain_experience(self.score // 10)  # XP basée sur le score

    def run(self):
        """Boucle principale de la phase de défense"""
        clock = pygame.time.Clock()
        running = True

        # Sélectionner la première potion si disponible
        if self.available_potions:
            self.launcher.select_potion(self.available_potions[0])

        while running:
            # Gérer les événements
            running = self.handle_events()

            # Calculer le delta temps
            dt = clock.tick(60) / 1000.0

            # Mettre à jour le jeu
            self.update(dt)

            # Dessiner tous les éléments
            self.draw()

            # Vérifier si la partie est terminée
            if self.laboratory.health <= 0:
                # Attendre un peu avant de quitter
                pygame.time.delay(3000)
                break

        # Retourner le score pour la phase suivante
        return self.score, self.wave