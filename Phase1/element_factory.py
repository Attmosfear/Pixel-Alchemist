from Phase1.elements import Element


class ElementFactory:
    """
    Classe responsable de la création d'éléments dans le jeu
    """

    @staticmethod
    def create_base_element(game, zone_name):
        """
        Crée un élément de base en fonction du nom de la zone
        :param game: Instance de la classe Game
        :param zone_name: Nom de la zone (Feu, Eau, Terre, Air)
        :return: L'élément créé ou None si la création a échoué
        """
        # Trouver la donnée de l'élément correspondant au nom de la zone
        element_data = None
        for data in game.elements_data:
            if data["name"] == zone_name:
                element_data = data
                break

        if element_data is None:
            print(f"DEBUG: Aucune donnée trouvée pour l'élément {zone_name}")
            return None

        # Créer l'élément
        # Trouver la zone de création correspondante
        creation_zone = None
        for zone in game.creation_zones:
            if zone.name == zone_name:
                creation_zone = zone
                break

        if creation_zone is None:
            print(f"DEBUG: Aucune zone trouvée pour créer l'élément {zone_name}")
            return None

        # Créer l'élément directement à la position du joueur pour faciliter la récupération
        new_element = Element(game.player.rect.centerx, game.player.rect.centery, element_data)
        new_element.held_by_player = True  # Marquer comme étant déjà tenu par le joueur
        game.elements.add(new_element)

        print(f"DEBUG: Élément {zone_name} créé et assigné au joueur")
        return new_element