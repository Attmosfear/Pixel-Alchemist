import pygame

from Phase1.elements import Element


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('Assets/Art/player.png').convert()
        self.image = self.get_image(0,0)
        self.rect = self.image.get_rect()
        self.position = [x, y]
        self.speed = 2
        self.velocity = [0, 0]
        self.feet = pygame.Rect(0,0, self.rect.width * 0.5, 12)
        self.old_position = self.position.copy()
        self.direction = 'DOWN'
        # Ajout d’un inventaire pour porter un objet
        self.held_item : Element = None


    def save_location(self): self.old_position = self.position.copy()

    def get_image(self, x, y):
        image = pygame.Surface([25, 30])
        image.blit(self.sprite_sheet, (0, 0), (x, y, 16, 16))
        return image

    def move(self):
        self.position[0] += self.velocity[0] * self.speed
        self.position[1] += self.velocity[1] * self.speed

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    """Gestion des objets"""


    def pick_element(self, element):
        print("Objet recuperer")
        self.held_item = element
        element.held_by_player = True

    def drop_element(self, zone):
        print("Objet deposer")
        self.held_item.held_by_player = False
        self.held_item = None
        zone.have_object = True

    def update(self):
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom