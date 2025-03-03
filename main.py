import pygame
import pyscroll
from player import Player
import pytmx


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()

        # Chargement du joueur
        self.player = Player(240, 160)

        self.tmx_data = pytmx.util_pygame.load_pygame("Assets/Map/Maptest.tmx")
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=2)

    def handling_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.velocity[0] = -1
        elif keys[pygame.K_RIGHT]:
            self.player.velocity[0] = 1
        else:
            self.player.velocity[0] = 0

        if keys[pygame.K_UP]:
            self.player.velocity[1] = -1
        elif keys[pygame.K_DOWN]:
            self.player.velocity[1] = 1
        else:
            self.player.velocity[1] = 0

    def update(self):
        # Sauvegarde de la position précédente
        old_position = self.player.rect.copy()

        # Déplacement du joueur
        self.player.move()

        # Récupération des dimensions de l'écran
        screen_width, screen_height = self.screen.get_size()

        # Supposons que le joueur a une taille (width, height) dans son rect
        player_width = self.player.rect.width
        player_height = self.player.rect.height

        # Vérification des bordures
        if self.player.rect.left < 0:
            self.player.rect.left = 0
        if self.player.rect.right > screen_width:
            self.player.rect.right = screen_width
        if self.player.rect.top < 0:
            self.player.rect.top = 0
        if self.player.rect.bottom > screen_height:
            self.player.rect.bottom = screen_height

    def display(self):
        # Dessiner le groupe de calques
        self.group.draw(self.screen)
        self.player.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handling_events()
            self.update()
            self.display()
            self.clock.tick(60)

pygame.init()
pygame.display.set_caption("Pixel-Alchemist")
screen = pygame.display.set_mode((960, 640))
game = Game(screen)
game.run()