import pygame
import math
import random  # Nécessaire pour la sélection aléatoire de conseils
import os
from Phase2.enemy import EnemyManager
from Phase2.launcher import Launcher
from Phase2.laboratory import Laboratory
from Phase2.effects import EffectManager
from constants import *

class DefenseGame:
    """Classe principale pour la phase de défense du laboratoire"""

    def __init__(self, screen, player, potions):
        self.screen = screen
        self.player = player
        self.native_surface = pygame.Surface((800, 600))  # Plus grande pour la phase de défense

        # Récupération des potions créées dans la phase 1
        self.available_potions = list(potions)

        self.game_over_state = False  # Indique si le jeu est terminé
        self.restart_game = False  # Indique si le joueur souhaite recommencer
        self.exit_to_lab = False  # Indique si le joueur souhaite retourner au laboratoire

        # Définir une hauteur de sol fixe à 448-128 = 320 pixels
        self.floor_level = 425 # Hauteur par défaut du sol

        # Charger le background PNG pour la phase 2
        try:
            self.background = pygame.image.load('Assets/Map/Map Main 2.png').convert()
            print("Background PNG chargé avec succès pour la phase de défense!")
        except FileNotFoundError:
            # En cas d'erreur, créer un background par défaut
            print("Image map_main_2.png non trouvée. Utilisation d'un background par défaut.")
            self.background = pygame.Surface((800, 600))
            self.background.fill((100, 150, 255))  # Fond bleu ciel

            # Sol
            pygame.draw.rect(self.background, (100, 70, 0), (0, self.floor_level, 800, 600 - self.floor_level))

            # Quelques éléments de décor basiques
            # Montagnes en arrière-plan
            for i in range(5):
                x = 100 + i * 160
                height = 80 + random.randint(0, 40)
                pygame.draw.polygon(self.background, (80, 80, 80),
                                    [(x - 60, self.floor_level), (x, self.floor_level - height),
                                     (x + 60, self.floor_level)])

            # Quelques nuages
            for i in range(3):
                x = 150 + i * 250
                y = 50 + random.randint(0, 100)
                pygame.draw.ellipse(self.background, (230, 230, 230), (x, y, 120, 40))
                pygame.draw.ellipse(self.background, (230, 230, 230), (x + 30, y - 20, 80, 40))

        # Adapter la taille si nécessaire
        if self.background.get_size() != (800, 600):
            self.background = pygame.transform.scale(self.background, (800, 600))

        # Laboratoire - positionné à une position fixe
        self.laboratory = Laboratory(50, self.floor_level - 145)  # Placé au-dessus du sol

        # Lanceur de potions - placé près du sol
        self.launcher = Launcher(100, self.floor_level - 20 , self.floor_level)  # Près du sol

        # Gestionnaire d'ennemis - avec le bon niveau de sol
        self.enemy_manager = EnemyManager(WINDOW_WIDTH, WINDOW_HEIGHT, self.floor_level)

        # Gestionnaire d'effets visuels
        self.effect_manager = EffectManager()

        # Gestionnaire d'effets visuels
        self.effect_manager = EffectManager()

        # État du jeu
        self.wave = 1
        self.score = 0

        # Interface
        self.font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 32)
        self.selected_potion_index = 0 if self.available_potions else -1

        # Sélectionner la première potion si disponible
        if self.available_potions and self.selected_potion_index >= 0:
            self.launcher.select_potion(self.available_potions[self.selected_potion_index])

        # Gestion du temps
        self.wave_timer = 0
        self.wave_duration = 60  # Durée d'une vague en secondes

    def handle_events(self):
        """Gère les événements clavier/souris"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pass

                # Si on est en état de game over, gérer les options spéciales
                if self.game_over_state:
                    if event.key == pygame.K_r:  # R pour recommencer
                        self.restart_game = True
                        return False  # Sortir de la boucle de jeu pour redémarrer

                    elif event.key == pygame.K_RETURN:  # Entrée pour retourner au laboratoire
                        running = False
                        return False  # Sortir de la boucle de jeu pour retourner au laboratoire

                    # Ignorer les autres touches en état de game over
                    continue

                # Changer la potion sélectionnée (avec les touches)
                elif event.key == pygame.K_LEFT:
                    if self.available_potions:
                        self.selected_potion_index = (self.selected_potion_index - 1) % len(self.available_potions)
                        self.launcher.select_potion(self.available_potions[self.selected_potion_index])

                elif event.key == pygame.K_RIGHT:
                    if self.available_potions:
                        self.selected_potion_index = (self.selected_potion_index + 1) % len(self.available_potions)
                        self.launcher.select_potion(self.available_potions[self.selected_potion_index])

                # Pour les joueurs qui préfèrent le clavier
                elif event.key == pygame.K_SPACE:
                    if not self.launcher.is_aiming:
                        self.launcher.is_aiming = True
                    else:
                        # Lancer la potion sélectionnée
                        used_potion = self.launcher.launch()
                        if used_potion in self.available_potions:
                            self.available_potions.remove(used_potion)
                            if self.available_potions:
                                self.selected_potion_index = min(self.selected_potion_index,
                                                                 len(self.available_potions) - 1)
                                self.launcher.select_potion(self.available_potions[self.selected_potion_index])
                            else:
                                self.selected_potion_index = -1
                                self.launcher.select_potion(None)

            # Gestion des événements de souris
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                # Déléguer au launcher
                result = self.launcher.handle_mouse_events(event)

                # Traiter le résultat
                if result == "prev_potion":
                    if self.available_potions:
                        self.selected_potion_index = (self.selected_potion_index - 1) % len(self.available_potions)
                        self.launcher.select_potion(self.available_potions[self.selected_potion_index])
                elif result == "next_potion":
                    if self.available_potions:
                        self.selected_potion_index = (self.selected_potion_index + 1) % len(self.available_potions)
                        self.launcher.select_potion(self.available_potions[self.selected_potion_index])
                elif result is not None:
                    # Une potion a été lancée, la retirer de la liste
                    used_potion = result
                    if used_potion in self.available_potions:
                        self.available_potions.remove(used_potion)
                        if self.available_potions:
                            self.selected_potion_index = min(self.selected_potion_index,
                                                             len(self.available_potions) - 1)
                            self.launcher.select_potion(self.available_potions[self.selected_potion_index])
                        else:
                            self.selected_potion_index = -1
                            self.launcher.select_potion(None)

        return True

    def update(self, dt):
        """Mise à jour de tous les éléments du jeu"""
        # Mise à jour du lanceur et des projectiles
        self.launcher.update(dt)

        # Mise à jour des ennemis
        self.enemy_manager.update(dt)

        # Mise à jour des effets visuels
        self.effect_manager.update(dt)

        # Mise à jour des effets visuels
        self.effect_manager.update(dt)

        # Appliquer les effets aux ennemis
        self.effect_manager.affect_enemies(self.enemy_manager.enemies, dt)

        # Vérifier les collisions entre projectiles et ennemis
        hits = self.launcher.check_collision_with_enemies(self.enemy_manager.enemies, self.effect_manager)
        for enemy, potion in hits:
            # Appliquer l'effet de la potion à l'ennemi
            enemy.apply_potion_effect(potion)

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
        # Dessiner le fond (simple PNG)
        self.screen.blit(self.background, (0, 0))

        # Dessiner le laboratoire
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
        # Dessiner un fond pour la sélection de potions
        pygame.draw.rect(self.screen, (50, 50, 50, 180), (0, 530, 800, 70))

        # Si aucune potion n'est disponible
        if not self.available_potions:
            info_text = self.font.render("Plus de potions ! Utilisez les pierres (clic gauche)", True, (255, 200, 200))
            self.screen.blit(info_text, (250, 555))
            return

        # Disposition des potions en barres d'inventaire
        potion_size = 40
        spacing = 10
        start_x = (self.screen.get_width() - (len(self.available_potions) * (potion_size + spacing))) // 2
        y = 545

        # Dessiner chaque potion
        for i, potion in enumerate(self.available_potions):
            x = start_x + i * (potion_size + spacing)

            # Cadre pour la potion sélectionnée
            if i == self.selected_potion_index:
                # Cadre plus visible avec animation légère
                pulse = (math.sin(pygame.time.get_ticks() * 0.01) * 0.5 + 0.5) * 255
                highlight_color = (255, 255, pulse)
                pygame.draw.rect(self.screen, highlight_color, (x - 3, y - 3, potion_size + 6, potion_size + 6), 3)

                # Afficher les détails de la potion sélectionnée en haut du panel
                selected_text = f"{potion.name} - {potion.effect}"
                details_text = self.font.render(selected_text, True, (255, 255, 255))
                self.screen.blit(details_text, (400 - details_text.get_width() // 2, 510))

            # Dessiner l'image de la potion
            try:
                potion_img = potion.image
                if potion_img.get_width() > potion_size or potion_img.get_height() > potion_size:
                    potion_img = pygame.transform.scale(potion_img, (potion_size, potion_size))
                self.screen.blit(potion_img, (x, y))
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
                pygame.draw.rect(self.screen, color, (x, y, potion_size, potion_size))

        # Instructions pour l'utilisation de la souris
        instructions = self.font.render(
            "Molette: Changer de potion | Clic gauche: Viser/Lancer", True, (200, 200, 200))
        self.screen.blit(instructions, (250, 580))

    def draw_game_over(self):
        """Affiche l'écran de fin de partie avec conseils et option de redémarrage"""
        # Overlay semi-transparent pour assombrir l'écran
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))  # Noir plus opaque pour meilleure lisibilité
        self.screen.blit(overlay, (0, 0))

        # Titre "GAME OVER" en gros et en rouge
        game_over_text = self.title_font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(game_over_text, (400 - game_over_text.get_width() // 2, 150))

        # Statistiques de la partie
        font_stats = pygame.font.SysFont('Arial', 22)

        # Score final
        score_text = font_stats.render(f"Score final : {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (400 - score_text.get_width() // 2, 210))

        # Vagues survécues
        wave_text = font_stats.render(f"Vagues survécues : {self.wave - 1}", True, (255, 255, 255))
        self.screen.blit(wave_text, (400 - wave_text.get_width() // 2, 240))

        # Générer un conseil utile en fonction de la performance du joueur
        font_tip = pygame.font.SysFont('Arial', 18)
        tip_text = self.get_game_over_tip()

        # Fond pour le conseil
        tip_bg = pygame.Surface((600, 70), pygame.SRCALPHA)
        tip_bg.fill((0, 0, 100, 180))  # Bleu foncé semi-transparent
        self.screen.blit(tip_bg, (100, 280))

        # Titre "Conseil"
        tip_title = font_tip.render("Conseil pour la prochaine partie :", True, (255, 255, 0))
        self.screen.blit(tip_title, (110, 290))

        # Le conseil lui-même
        tip = font_tip.render(tip_text, True, (255, 255, 255))
        self.screen.blit(tip, (110, 320))

        # Options pour le joueur
        font_options = pygame.font.SysFont('Arial', 24)

        # Option de redémarrage
        restart_text = font_options.render("Appuyez sur R pour recommencer", True, (0, 255, 0))
        self.screen.blit(restart_text, (400 - restart_text.get_width() // 2, 380))

        # Option de retour au laboratoire
        menu_text = font_options.render("Appuyez sur ENTRÉE pour retourner au laboratoire", True, (200, 200, 200))
        self.screen.blit(menu_text, (400 - menu_text.get_width() // 2, 420))

        # Petit message additionnel
        tip2_text = font_tip.render("N'oubliez pas de créer différents types de potions pour la prochaine défense !",
                                    True, (255, 200, 100))
        self.screen.blit(tip2_text, (400 - tip2_text.get_width() // 2, 470))

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

    def get_game_over_tip(self):
        """Génère un conseil en fonction de la performance du joueur"""
        # Plusieurs conseils possibles selon différentes situations de jeu
        tips = [
            "Utilisez les potions de ralentissement (Boue) pour avoir plus de temps pour viser",
            "Les potions de zone comme la Lave sont efficaces contre les groupes d'ennemis",
            "Alternez entre potions d'attaque et potions de statut pour maximiser l'effet",
            "Visez devant les ennemis pour qu'ils marchent dans vos flaques d'effet",
            "Essayez de créer des potions plus puissantes en combinant des éléments avancés",
            "Les ennemis volants sont plus faciles à toucher avec des potions à effet de zone",
            "Créez plus de potions pendant la phase 1 pour être mieux préparé",
            "Les potions de Cristal peuvent immobiliser les ennemis les plus coriaces"
        ]

        # Conseil spécifique si le joueur n'a pas survécu à la première vague
        if self.wave <= 1:
            return "Prenez votre temps pour viser. Les potions sont précieuses !"

        # Conseil spécifique si le joueur n'avait pas beaucoup de potions
        elif len(self.available_potions) == 0:
            return "Créez plus de potions pendant la phase de préparation pour mieux vous défendre"

        # Conseil spécifique si le joueur a atteint un score élevé
        elif self.score > 500:
            return "Votre stratégie fonctionne bien ! Essayez maintenant des combinaisons de potions plus complexes"

        # Sinon, conseil aléatoire
        else:
            return random.choice(tips)

    def game_over(self):
        """Gère la fin de partie"""
        # Les points bonus seront déjà comptabilisés dans le score

        # Sauvegarder les données dans le profil du joueur
        self.player.score += self.score
        self.player.gain_experience(self.score // 10)  # XP basée sur le score

        # Activer l'état de game over
        self.game_over_state = True

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

            # Si le joueur veut recommencer, indiquer qu'il faut redémarrer le jeu
            if self.restart_game:
                return "restart", self.score, self.wave

            # Si le joueur veut retourner au laboratoire après un game over
            if self.exit_to_lab:
                return self.score, self.wave

            # Calculer le delta temps
            dt = clock.tick(60) / 1000.0

            # Ne mettre à jour le jeu que s'il n'est pas en état de game over
            if not self.game_over_state:
                self.update(dt)

            # Dessiner tous les éléments
            self.draw()

            # Vérifier si le jeu est terminé
            if self.laboratory.health <= 0 and not self.game_over_state:
                # Activer l'état de game over
                self.game_over()

        # Retourner le score et la vague pour l'utilisation ultérieure
        return self.score, self.wave