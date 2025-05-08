from Phase1.elements import *


class Zone(pygame.sprite.Sprite):
    def __init__(self, x, y, id, type):
        super().__init__()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.id = id
        self.type = type
        self.have_object = False

def get_front_tile(player, zones):
    """
    Verifie la presence d'une tuile devant le joueur
    # :return: None s'il y en a pas ou la tuile si elle est presente
    """
    player_position = player.rect.center
    front_tile_position = (player_position[0], player_position[1] - 25)
    if player.direction == 'UP':
        front_tile_position = (player_position[0], player_position[1] - 15)
    elif player.direction == 'DOWN':
        front_tile_position = (player_position[0], player_position[1] + 25)
    elif player.direction == 'LEFT':
        front_tile_position = (player_position[0] - 25, player_position[1] )
    elif player.direction == 'RIGHT':
        front_tile_position = (player_position[0] + 25, player_position[1])

    for zone in zones:
        if  zone.rect.collidepoint(front_tile_position):
            print("La zone presente devant est ", zone.type, zone.id)
            return zone

    return None


def get_element_on_tile(zone, game_objects, potion_craft_state=None):
    """
    Permet de savoir quel objet est sur la zone demandée et gère les états si nécessaire
    :param zone: zone parmi les zones récupérées dans le fichier de la carte
    :param game_objects: un dictionnaire avec les différents groupes d'objets {'elements': elements_group, 'potions': potions_group, 'stones': stones_group}
    :param potion_craft_state: état du crafting de potion (optionnel)
    :return: l'objet présent sur la zone ou None
    """
    # Vérifier pour chaque type d'objet si l'un d'eux est sur la zone
    for object_type, object_group in game_objects.items():
        for obj in object_group:
            if obj.held_by_player:
                continue
            if zone.rect.colliderect(obj.rect):
                # Si on a un état de crafting de potion et que c'est une zone de crafting
                if potion_craft_state is not None and zone.type == "potioncraft_zone":
                    zone_id = zone.id
                    print(f"DEBUG: Récupération d'un objet ({object_type}) sur la zone {zone_id}")

                    # Réinitialiser l'état correspondant en fonction du type d'objet et de la zone
                    if zone_id == 36 and potion_craft_state["element"] == obj:
                        print("DEBUG: Réinitialisation de l'élément principal")
                        potion_craft_state["element"] = None
                    elif zone_id == 38 and potion_craft_state["stone1"] == obj:
                        print("DEBUG: Réinitialisation de la pierre 1")
                        potion_craft_state["stone1"] = None
                    elif zone_id == 39 and potion_craft_state["stone2"] == obj:
                        print("DEBUG: Réinitialisation de la pierre 2")
                        potion_craft_state["stone2"] = None
                    elif zone_id == 37 and potion_craft_state["result"] == obj:
                        print("DEBUG: Récupération de la potion résultante")
                        potion_craft_state["result"] = None

                # Indiquer que la zone n'a plus d'objet
                zone.have_object = False

                return obj

    return None

def create_base_element(self, zone_name):
    """
    rée un élément de base en fonction du nom de la zone
    :param zone_name: Nom de la zone (Feu, Eau, Terre, Air)
    :return: L'élément créé ou None si la création a échoué
    """
    # Trouver la donnée de l'élément correspondant au nom de la zone
    element_data = None
    for data in self.elements_data:
        if data["name"] == zone_name:
            element_data = data
            break

    if element_data is None:
        print(f"DEBUG: Aucune donnée trouvée pour l'élément {zone_name}")
        return None

    # Créer l'élément
    # Trouver la zone de création correspondante
    creation_zone = None
    for zone in self.creation_zones:
        if zone.name == zone_name:
            creation_zone = zone
            break

    if creation_zone is None:
        print(f"DEBUG: Aucune zone trouvée pour créer l'élément {zone_name}")
        return None

    # Créer l'élément au centre de la zone
    new_element = Element(creation_zone.rect.centerx, creation_zone.rect.centery, element_data)
    self.elements.add(new_element)

    print(f"DEBUG: Élément {zone_name} créé")