import pygame
import pyscroll


from player import Player
import pytmx


class Ice(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Assets/Map/ice.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.held = False


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()

        self.native_surface = pygame.Surface((NATIVE_WIDTH, NATIVE_HEIGHT))


        # Chargement de la carte
        tmx_data = pytmx.util_pygame.load_pygame("Assets/Map/Maptest.tmx")
        map_date = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_date, (NATIVE_WIDTH, NATIVE_HEIGHT))

        #Chargement du joueur
        self.player = Player(30,30)

        # Chargement du glaçon
        self.ice = Ice(100, 100)

        """Gestion des collisions"""
        # Recuperation des rectangles de collision dans une liste
        self.walls = []
        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        # Ajout des bords de l'écran comme des collisions
        screen_width, screen_height = NATIVE_WIDTH, NATIVE_HEIGHT
        self.walls.append(pygame.Rect(-5, 0, 5, screen_height))
        self.walls.append(pygame.Rect(screen_width, 0, 5, screen_height))
        self.walls.append(pygame.Rect(0, -5, screen_width, 5))
        self.walls.append(pygame.Rect(0, screen_height, screen_width, 5))

        #Dessiner le groupe de calques
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=2)
        self.group.add(self.player, self.ice)

        self.holding_ice = False

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

        # Interaction avec le glaçon
        if keys[pygame.K_e] and not self.holding_ice:
            if self.player.rect.colliderect(self.ice.rect):
                self.holding_ice = True
                self.ice.held = True

        if keys[pygame.K_f] and self.holding_ice:
            self.holding_ice = False
            self.ice.held = False
            self.ice.rect.topleft = self.player.rect.topleft

    def update(self):

        # Déplacement du joueur
        self.player.move()
        self.player.update()

        if self.holding_ice:
            self.ice.rect.center = self.player.rect.center

        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()

    def display(self):
        self.native_surface.fill((100, 100, 100))
        self.group.update()
        self.group.center(self.player.rect.center)
        self.group.draw(self.native_surface)

        # Redimensionner la surface et l'afficher sur l'écran
        scaled_surface = pygame.transform.scale(self.native_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.player.save_location()
            self.handling_events()
            self.update()
            self.display()
            self.clock.tick(60)

"""Gestion du scaling de l'ecran"""
#Taille native de la carte
NATIVE_WIDTH, NATIVE_HEIGHT = 320, 224
#Taille de la fenetre affichée
SCALE = 3 # Definir dans les parametres du jeu ou en fonction de l'ecran du joueur
WINDOW_WIDTH = NATIVE_WIDTH * SCALE
WINDOW_HEIGHT = NATIVE_HEIGHT * SCALE

pygame.init()
pygame.display.set_caption("Pixel-Alchemist")
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
game = Game(screen)
game.run()