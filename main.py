import pygame
import pyscroll
from player import Player
import pytmx


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()

        # Chargement de la carte
        tmx_data = pytmx.util_pygame.load_pygame("Assets/Map/Maptest.tmx")
        map_date = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_date, self.screen.get_size())

        #Chargement du joueur
        self.player = Player(30,30)

        """Gestion des collisions"""
        # Recuperation des rectangles de collision dans une liste
        self.walls = []
        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        # Ajout des bords de l'écran comme des collisions
        screen_width, screen_height = self.screen.get_size()
        self.walls.append(pygame.Rect(-5, 0, 5, screen_height))
        self.walls.append(pygame.Rect(screen_width, 0, 5, screen_height))
        self.walls.append(pygame.Rect(0, -5, screen_width, 5))
        self.walls.append(pygame.Rect(0, screen_height, screen_width, 5))

        #Dessiner le groupe de calques
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=2)
        self.group.add(self.player)

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

        # Déplacement du joueur
        self.player.move()
        self.player.update()

        #Verification de collision
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()

    def display(self):
        self.group.update()
        self.group.center(self.player.rect.center)
        self.group.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.player.save_location()
            self.handling_events()
            self.update()
            self.display()
            self.clock.tick(60)

pygame.init()
pygame.display.set_caption("Pixel-Alchemist")
screen = pygame.display.set_mode((320, 224))
game = Game(screen)
game.run()