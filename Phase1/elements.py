import pygame
import os
class Element(pygame.sprite.Sprite):
    def __init__(self, x, y, element_data):
        """
        Initialise un élément à partir des données JSON.
        :param x: Position X
        :param y: Position Y
        :param element_data: Dictionnaire contenant les infos les elements
        """
        super().__init__()

        # Vérifier que element_data est bien un dictionnaire
        if not isinstance(element_data, dict):
            raise TypeError(f"element_data doit être un dictionnaire, reçu {type(element_data)} : {element_data}")


        self.id = element_data["id"]
        self.name = element_data["name"]
        self.texture = element_data["texture"]
        self.tier = element_data["tier"]
        self.ingredients = element_data["ingredients"] # Peut être None

        # Chargement de l'image
        chemin_image = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(os.path.dirname(__file__)))), "Pixel-Alchemist", "Assets", "Art", "Items", "Elements", self.texture)
        self.image = pygame.image.load(chemin_image).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        print("Image chargée :", self.image.get_size())  # Vérifie la taille de l'image

        self.held_by_player = False

    def update_position(self, player):
        """Met à jour la position de l'élément quand il est porté par le joueur"""
        if self.held_by_player:
            # Offsets adaptés pour l'affichage sans zoom
            offset_x, offset_y = 0, 0

            # Positions relatives en fonction de la direction du joueur
            if player.direction == "UP":
                offset_y = -20
            elif player.direction == "DOWN":
                offset_y = 20
            elif player.direction == "LEFT":
                offset_x = -20
            elif player.direction == "RIGHT":
                offset_x = 20

            # Positionner l'élément par rapport au centre du joueur
            self.rect.centerx = player.rect.centerx + offset_x
            self.rect.centery = player.rect.centery + offset_y

    def update(self):
        pass  # Peut être utilisé plus tard pour des animations