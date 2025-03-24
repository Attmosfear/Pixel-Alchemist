import pygame

class Element(pygame.sprite.Sprite):
    def __init__(self, x, y, element_data):
        """
        Initialise un élément à partir des données JSON.
        :param x: Position X
        :param y: Position Y
        :param element_data: Dictionnaire contenant les infos de l'élément
        """
        super().__init__()

        # Vérifier que element_data est bien un dictionnaire
        if not isinstance(element_data, dict):
            raise TypeError(f"element_data doit être un dictionnaire, reçu {type(element_data)} : {element_data}")


        self.id = element_data["id"]
        self.name = element_data["name"]
        self.texture = element_data["texture"]
        self.tier = element_data["tier"]
        self.ingredients = element_data["ingredients"]  # Peut être None

        # Chargement de l'image
        self.image = pygame.image.load(f"../Assets/Art/Items/Blocks/{self.texture}").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        pass  # Peut être utilisé plus tard pour des animations