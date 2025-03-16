import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('Assets/Art/playerTest.png').convert()
        self.image = self.get_image(0,0)
        self.rect = self.image.get_rect()
        self.position = [x, y]
        self.speed = 5
        self.velocity = [0, 0]
        self.feet = pygame.Rect(0,0, self.rect.width * 0.5, 12)
        self.old_position = self.position.copy()



    def save_location(self): self.old_position = self.position.copy()

    def get_image(self, x, y):
        image = pygame.Surface([16, 16])
        image.blit(self.sprite_sheet, (0, 0), (x, y, 16, 16))
        return image

    def move(self):
        self.position[0] += self.velocity[0] * self.speed
        self.position[1] += self.velocity[1] * self.speed

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def update(self):
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom
