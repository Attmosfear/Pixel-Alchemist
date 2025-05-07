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

    def check_for_crafting(self):
        """Vérifie si des éléments sont sur la table de craft et lance le crafting si nécessaire"""
        if self.craft_in_progress:
            return

        # Collecter les éléments sur les zones de craft
        elements_on_craft = []
        craft_center_x, craft_center_y = 0, 0

        for zone in self.game.craft_zones:
            if zone.have_object:
                # Chercher l'élément sur cette zone
                for element in self.game.elements:
                    if not element.held_by_player and zone.rect.colliderect(element.rect):
                        elements_on_craft.append(element)
                        # Calculer le centre pour l'animation
                        craft_center_x += zone.rect.centerx
                        craft_center_y += zone.rect.centery
                        break

        # S'il y a exactement 2 éléments, lancer le crafting automatique
        if len(elements_on_craft) == 2:
            # Calculer le centre moyen pour l'animation
            craft_center_x //= len(elements_on_craft)
            craft_center_y //= len(elements_on_craft)
            self.craft_center = (craft_center_x, craft_center_y)

            # Vérifier s'il existe une recette pour ces éléments
            recipe = self.game.check_block_craft(elements_on_craft, self.game.recipes_data)

            if recipe:
                self.craft_in_progress = True
                self.craft_timer = 0
                self.elements_to_craft = elements_on_craft

                # Ajouter l'animation
                craft_anim = CraftingAnimation(duration=self.craft_time_required)
                self.game.animation_manager.add_animation(
                    "element_crafting",
                    craft_anim,
                    self.craft_center
                )

                self.game.ui.show_message("Crafting en cours...", 2.0)

    def update(self, dt):
        """Met à jour le processus de crafting"""
        if not self.craft_in_progress:
            return

        self.craft_timer += dt

        # Vérifier si le temps requis est écoulé
        if self.craft_timer >= self.craft_time_required:
            self.craft_in_progress = False
            self.craft_timer = 0
            self.complete_crafting()

    def complete_crafting(self):
        """Termine le processus de crafting en créant le nouvel élément"""
        if not self.elements_to_craft or len(self.elements_to_craft) != 2:
            self.game.animation_manager.remove_animation("element_crafting")
            return

        # Vérifier à nouveau qu'il existe une recette pour ces éléments
        recipe = self.game.check_block_craft(self.elements_to_craft, self.game.recipes_data)

        if recipe:
            # Supprimer les éléments utilisés
            for element in self.elements_to_craft:
                self.game.elements.remove(element)

                # Marquer les zones comme libres
                for zone in self.game.craft_zones:
                    if zone.rect.colliderect(element.rect):
                        zone.have_object = False

            # Trouver les données de l'élément résultant
            result_data = next(e for e in self.game.elements_data if e["id"] == recipe['result'])

            # Créer le nouvel élément au centre de la table de craft
            if self.craft_center:
                new_element = Element(self.craft_center[0], self.craft_center[1], result_data)
                self.game.elements.add(new_element)

                # Marquer la zone comme occupée
                # On choisit arbitrairement la première zone de craft pour y placer le résultat
                if self.game.craft_zones:
                    self.game.craft_zones[0].have_object = True

                # Donner de l'XP au joueur
                self.game.player.gain_experience(5)
                self.game.ui.show_message(f"Élément {recipe['result_name']} créé!", 3.0)

        # Réinitialiser
        self.elements_to_craft = []
        self.craft_center = None
        self.game.animation_manager.remove_animation("element_crafting")


def check_block_craft(elements, recipes):
    """
    Vérifie si une combinaison d'éléments correspond à une recette
    :param elements: Liste des éléments à vérifier
    :param recipes: Liste des recettes disponibles
    :return: La recette correspondante ou None
    """
    posed_ids = sorted([el.id for el in elements])

    for recipe in recipes:
        if sorted(recipe["ingredients"]) == posed_ids:
            return recipe  # On retourne toute la recette
    return None

class PotionCraftManager:
    def __init__(self, potions_data):
        """
        Initialise le gestionnaire de crafting de potions
        :param potions_data: Liste des données de potions depuis le JSON
        """
        self.potions_data = potions_data
        # Structure pour stocker les éléments sur la table de craft de potions
        # Format: {"element": Element, "enhancements": [Enhancement1, Enhancement2]}
        self.potion_craft_elements = {"element": None, "enhancements": []}

        # Types d'améliorations possibles
        self.enhancement_types = ["power", "duration"]

    def add_element(self, element, zone_position):
        """
        Ajoute un élément dans la zone de crafting de potions
        :param element: L'élément à ajouter
        :param zone_position: Position de la zone (bottom_left, bottom_right, top_left, top_right)
        """
        if zone_position == "bottom_left":
            # Cette position est réservée à l'élément principal
            if self.potion_craft_elements["element"] is None:
                self.potion_craft_elements["element"] = element
                return True
        elif zone_position in ["top_left", "top_right"]:
            # Ces positions sont pour les améliorations
            if len(self.potion_craft_elements["enhancements"]) < 2:
                self.potion_craft_elements["enhancements"].append(element)
                return True

        return False  # L'ajout a échoué

    def remove_element(self, zone_position):
        """
        Retire un élément de la zone de crafting
        :param zone_position: Position de la zone
        :return: L'élément retiré ou None
        """
        if zone_position == "bottom_left" and self.potion_craft_elements["element"]:
            element = self.potion_craft_elements["element"]
            self.potion_craft_elements["element"] = None
            return element
        elif zone_position in ["top_left", "top_right"] and self.potion_craft_elements["enhancements"]:
            # Pour simplifier, on retire la dernière amélioration ajoutée
            return self.potion_craft_elements["enhancements"].pop()

        return None

    def craft_potion(self):
        """
        Tente de créer une potion avec les éléments présents
        :return: La potion créée ou None si le craft a échoué
        """
        if not self.potion_craft_elements["element"]:
            return None

        element_name = self.potion_craft_elements["element"].name

        # Recherche d'une potion correspondant à cet élément
        matching_potion = None
        for potion in self.potions_data:
            # Pour l'instant, on vérifie juste si le nom de l'élément correspond au nom de la potion
            # Plus tard, on pourra utiliser les ingrédients complets
            if element_name in potion["name"]:
                matching_potion = potion
                break

        if not matching_potion:
            return None

        # Création de la potion
        result_potion = Potion(0, 0, matching_potion)

        # Application des améliorations
        for i, enhancement in enumerate(self.potion_craft_elements["enhancements"]):
            enhancement_type = self.enhancement_types[i % len(self.enhancement_types)]
            result_potion.apply_enhancement(enhancement_type)

        # Réinitialiser la table après le craft
        self.potion_craft_elements = {"element": None, "enhancements": []}

        return result_potion

    def get_zone_position(self, zone):
        """
        Détermine la position relative d'une zone dans la table de craft
        :param zone: La zone à analyser
        :return: La position relative (bottom_left, bottom_right, top_left, top_right)
        """
        # Cette fonction suppose que les zones sont disposées en carré 2x2
        # bottom_left: élément principal
        # top_left, top_right: améliorations
        # bottom_right: résultat de la potion

        # À adapter selon la structure exacte de vos zones dans la carte TMX
        zone_ids = sorted([z.id for z in zone.parent.potioncraft_zone])

        if zone.id == zone_ids[0]:  # Première zone = bottom_left
            return "bottom_left"
        elif zone.id == zone_ids[1]:  # Deuxième zone = bottom_right
            return "bottom_right"
        elif zone.id == zone_ids[2]:  # Troisième zone = top_left
            return "top_left"
        elif zone.id == zone_ids[3]:  # Quatrième zone = top_right
            return "top_right"

        return None