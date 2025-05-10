import pygame
import os


class Potion(pygame.sprite.Sprite):
    def __init__(self, x, y, potion_data, element_name=None):
        """
        Initialise une potion à partir des données JSON.
        :param x: Position X
        :param y: Position Y
        :param potion_data: Dictionnaire contenant les infos des potions
        :param element_name: Nom de l'élément utilisé pour créer la potion (optionnel)
        """
        super().__init__()

        self.id = potion_data["id"]
        self.name = potion_data["name"]
        self.ingredients = potion_data["ingredients"]
        self.effect = potion_data["effect"]
        self.category = potion_data["category"]

        # Chemin pour l'image de la potion
        texture_name = f"{self.name.lower()}_potion.png"
        chemin_image = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(os.path.dirname(__file__)))),
                                    "Pixel-Alchemist", "Assets", "Art", "Items", "Potions", texture_name)

        # Essaye de charger l'image spécifique, sinon charge une image par défaut
        try:
            self.image = pygame.image.load(chemin_image).convert_alpha()
        except FileNotFoundError:
            # Charge une image par défaut si l'image spécifique n'existe pas
            default_image = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(os.path.dirname(__file__)))),
                                         "Pixel-Alchemist", "Assets", "Art", "Items", "Potions", "default_potion.png")
            self.image = pygame.image.load(default_image).convert_alpha()

        self.rect = self.image.get_rect(topleft=(x, y))

        # Attributs pour le gameplay
        self.held_by_player = False
        self.power = 1  # Puissance de base, peut être améliorée par des pierres
        self.duration = 1  # Durée de base, peut être améliorée par des pierres

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

    def apply_enhancement(self, enhancement_type):
        """
        Applique une amélioration à la potion
        :param enhancement_type: Type d'amélioration ("power" ou "duration")
        """
        if enhancement_type == "power":
            self.power += 1
        elif enhancement_type == "duration":
            self.duration += 1

        # Mise à jour visuelle (optionnelle)
        if self.power > 1 or self.duration > 1:
            # Ajouter un effet visuel pour montrer que la potion est améliorée
            # Par exemple, changer la couleur ou ajouter un effet de brillance
            pass

    def update(self):
        pass  # Pour des animations futures