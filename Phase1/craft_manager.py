from Phase1.potions import Potion

def check_block_craft(posed_elements, recipes):
    """
    posed_elements : liste des éléments posés sur la table de craft
    recipes : liste des recettes (chargées depuis recipes.json)
    """
    posed_ids = sorted([el.id for el in posed_elements])



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