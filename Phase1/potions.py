import pygame

class Potion(pygame.sprite.Sprite):
    def __init__(self, x, y, potions_data):
        """
        Initialise un élément à partir des données JSON.
        :param x: Position X
        :param y: Position Y
        :param potions_data: Dictionnaire contenant les infos des potions
        """
        super().__init__()

