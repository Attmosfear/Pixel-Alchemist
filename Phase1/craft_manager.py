from Phase1.potions import Potion
import pygame
from Phase1.animations import Animation, AnimationManager
from Phase1.elements import Element


class CraftingAnimation(Animation):
    """Animation pour le crafting automatique d'éléments"""

    def __init__(self, duration=2.0):
        super().__init__(duration)
        self.particles = []
        for i in range(10):
            # Créer des particules avec positions et couleurs aléatoires
            self.particles.append({
                'x': 0, 'y': 0,  # Seront mis à jour lors du dessin
                'angle': i * 36,
                'radius': 2 + i % 3,
                'color': (200 + i % 55, 100 + i % 155, 50 + i % 205)
            })

    def draw(self, surface, position):
        """Dessine l'animation de crafting"""
        center_x, center_y = position
        progress = self.get_progress()

        # Dessiner des particules qui tournent
        for particle in self.particles:
            angle = particle['angle'] + progress * 720  # 2 rotations complètes
            radius = 5 + particle['radius'] + progress * 15
            x = center_x + radius * pygame.math.Vector2(1, 0).rotate(angle).x
            y = center_y + radius * pygame.math.Vector2(1, 0).rotate(angle).y

            # Faire grossir puis rétrécir les particules
            size = int(particle['radius'] * (1 - abs(progress - 0.5) * 2)) + 2

            pygame.draw.circle(surface, particle['color'], (int(x), int(y)), size)

        # Afficher le progrès
        if progress < 1.0:
            font = pygame.font.SysFont('Arial', 12)
            progress_percent = int(progress * 100)
            text_surface = font.render(f"{progress_percent}%", True, (255, 255, 255))
            surface.blit(
                text_surface,
                (center_x - text_surface.get_width() // 2, center_y - 20)
            )


class AutoCraftManager:
    """Gestionnaire pour le crafting automatique d'éléments"""

    def __init__(self, game):
        self.game = game
        self.craft_in_progress = False
        self.craft_timer = 0
        self.craft_time_required = 2.0
        self.craft_center = None
        self.elements_to_craft = []
        self.matching_recipe = None  # Initialisé à None pour éviter les erreurs

    def check_for_crafting(self):
        """Vérifie si des éléments sont sur la table de craft et lance le crafting si nécessaire"""
        if self.craft_in_progress:
            return False

        # Pour une table 1x2, on doit avoir exactement 2 zones avec des éléments
        if len(self.game.craft_zones) != 2:
            print(f"DEBUG: Table de craft incorrecte - {len(self.game.craft_zones)} zones au lieu de 2")
            return False

        # Collecter les éléments sur les zones de craft
        elements_on_craft = []
        zones_with_elements = []

        # Vérifier les deux zones
        for zone in self.game.craft_zones:
            print(f"DEBUG: Vérification zone {zone.id}, occupée: {zone.have_object}")
            if zone.have_object:
                # Chercher l'élément sur cette zone
                for element in self.game.elements:
                    if not element.held_by_player and zone.rect.colliderect(element.rect):
                        elements_on_craft.append(element)
                        zones_with_elements.append(zone)
                        print(f"DEBUG: Élément {element.name} trouvé sur zone {zone.id}")
                        break

        # S'il y a exactement 2 éléments, lancer le crafting automatique
        if len(elements_on_craft) == 2:
            print(
                f"DEBUG: 2 éléments trouvés pour crafting: {elements_on_craft[0].name} et {elements_on_craft[1].name}")

            # Calculer le centre entre les deux zones pour l'animation
            craft_center_x = (zones_with_elements[0].rect.centerx + zones_with_elements[1].rect.centerx) // 2
            craft_center_y = (zones_with_elements[0].rect.centery + zones_with_elements[1].rect.centery) // 2
            self.craft_center = (craft_center_x, craft_center_y)

            # Vérifier s'il existe une recette pour ces éléments
            posed_ids = sorted([el.id for el in elements_on_craft])

            # Trouver une recette correspondante
            self.matching_recipe = None  # Réinitialiser
            for recipe in self.game.recipes_data:
                if sorted(recipe["ingredients"]) == posed_ids:
                    self.matching_recipe = recipe
                    break

            if self.matching_recipe:
                print("DEBUG: Recette trouvée pour auto-craft:", self.matching_recipe["result_name"])
                self.craft_in_progress = True
                self.craft_timer = 0
                self.elements_to_craft = elements_on_craft
                self.zones_with_elements = zones_with_elements

                # Ajouter l'animation
                craft_anim = CraftingAnimation(duration=self.craft_time_required)
                self.game.animation_manager.add_animation(
                    "element_crafting",
                    craft_anim,
                    self.craft_center
                )

                self.game.ui.show_message(f"Crafting {self.matching_recipe['result_name']} en cours...", 2.0)
                return True
            else:
                print("DEBUG: Pas de recette trouvée pour ces éléments")
        else:
            print(f"DEBUG: Nombre d'éléments insuffisant pour crafting: {len(elements_on_craft)}")

        return False

    def update(self, dt):
        """Met à jour le processus de crafting"""
        if not self.craft_in_progress:
            return

        self.craft_timer += dt
        print(f"DEBUG: Timer crafting: {self.craft_timer:.2f}/{self.craft_time_required}")

        # Vérifier si le temps requis est écoulé
        if self.craft_timer >= self.craft_time_required:
            self.craft_in_progress = False
            self.craft_timer = 0
            self.complete_crafting()

    def complete_crafting(self):
        """Termine le processus de crafting en créant le nouvel élément"""
        if self.matching_recipe is None or not self.elements_to_craft or len(self.elements_to_craft) != 2:
            print("DEBUG: Impossible de compléter le crafting - données manquantes")
            self.game.animation_manager.remove_animation("element_crafting")
            return

        # Supprimer les éléments utilisés
        for element in self.elements_to_craft:
            self.game.elements.remove(element)
            print(f"DEBUG: Élément {element.name} consommé dans le crafting")

        # Libérer les zones
        if hasattr(self, 'zones_with_elements'):
            for zone in self.zones_with_elements:
                zone.have_object = False
                print(f"DEBUG: Zone {zone.id} libérée")

        # Trouver les données de l'élément résultant
        result_data = next(e for e in self.game.elements_data if e["id"] == self.matching_recipe['result'])

        # Créer le nouvel élément au centre calculé
        if self.craft_center:
            new_element = Element(self.craft_center[0], self.craft_center[1], result_data)
            self.game.elements.add(new_element)
            print(f"DEBUG: Nouvel élément {self.matching_recipe['result_name']} créé à {self.craft_center}")

            # Marquer une des zones comme occupée par le nouvel élément
            if hasattr(self, 'zones_with_elements') and len(self.zones_with_elements) > 0:
                self.zones_with_elements[0].have_object = True
                print(f"DEBUG: Zone {self.zones_with_elements[0].id} marquée comme occupée par le nouvel élément")

            # Donner de l'XP au joueur
            self.game.player.gain_experience(5)
            self.game.ui.show_message(f"Élément {self.matching_recipe['result_name']} créé!", 3.0)

        # Réinitialiser
        self.elements_to_craft = []
        self.craft_center = None
        self.matching_recipe = None
        if hasattr(self, 'zones_with_elements'):
            delattr(self, 'zones_with_elements')
        self.game.animation_manager.remove_animation("element_crafting")


def check_block_craft(posed_elements, recipes):
    """
    Vérifie si une combinaison d'éléments correspond à une recette
    :param posed_elements : liste des éléments posés sur la table de craft
    :param recipes : liste des recettes (chargées depuis recipes.json)
    """
    posed_ids = sorted([el.id for el in posed_elements])

    for recipe in recipes:
        if sorted(recipe["ingredients"]) == posed_ids:
            return recipe  # On retourne toute la recette
    return None