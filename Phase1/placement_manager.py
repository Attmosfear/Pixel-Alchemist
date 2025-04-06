from zoneinfo import ZoneInfo

import pygame

class Zone(pygame.sprite.Sprite):
    def __init__(self, x, y, id, type):
        super().__init__()
        self.rect = pygame.Rect(x, y, 32, 32)
        self.id = id
        self.type = type
        self.have_object = False

def get_front_tile(player, zones):
    """
    Verifie la presence du tile devant le joueur
    # :return: None s'il y en a pas ou la tile si elle est presente
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

def get_element_on_tile(zone, elements):
    """

    :param zone:
    :param elements:
    :return:
    """
    for element in elements:
        if zone.rect.colliderect(element.rect):
            return element
