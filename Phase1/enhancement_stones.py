import pygame
import os


class EnhancementStone(pygame.sprite.Sprite):
    def __init__(self, x, y, stone_type):
        """
        Initialise une pierre d'amélioration
        :param x: Position X
        :param y: Position Y
        :param stone_type: Type de pierre ("power" ou "duration")
        """
        super().__init__()

        self.stone_type = stone_type

        # Chargement de l'image
        image_name = f"{stone_type}_stone.png"
        chemin_image = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(os.path.dirname(__file__)))),
                                    "Pixel-Alchemist", "Assets", "Art", "Items", "Stones", image_name)

        # Essaye de charger l'image spécifique, sinon charge une image par défaut
        try:
            self.image = pygame.image.load(chemin_image).convert_alpha()
        except FileNotFoundError:
            # Crée une image de remplacement si l'image n'existe pas
            self.image = pygame.Surface((20, 20))
            if stone_type == "power":
                self.image.fill((255, 0, 0))  # Rouge pour la puissance
            else:
                self.image.fill((0, 0, 255))  # Bleu pour la durée

        self.rect = self.image.get_rect(topleft=(x, y))

        # Attributs
        self.held_by_player = False

    def update_position(self, player):
        """Met à jour la position de la pierre quand elle est portée par le joueur"""
        if self.held_by_player:
            offset_x, offset_y = 0, 0
            if player.direction == "UP":
                offset_y = -15
            elif player.direction == "DOWN":
                offset_y = 15
            elif player.direction == "LEFT":
                offset_x = -20
            elif player.direction == "RIGHT":
                offset_x = 20

            self.rect.centerx = player.rect.centerx + offset_x
            self.rect.centery = player.rect.centery + offset_y

    def update(self):
        pass