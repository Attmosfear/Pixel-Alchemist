import pygame

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
        self.direction = 'down'
        # Ajout d’un inventaire pour porter un objet
        self.held_item = None


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

    def update(self):
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    """Gestion des objets"""
    def pick_up(self, item):
        #Le joueur prend un objet s’il n’en porte pas déjà un
        if self.held_item is None:
            self.held_item = item
            print(f"Objet ramassé : {item}")


    def drop_item(self):
        #Le joueur dépose son objet

        if self.held_item:
            print(f"Objet {self.held_item} posé")
            item = self.held_item
            self.held_item = None  # Vide les mains du joueur
            return item
        return None  # Aucun objet à poser

    def get_front_tile(self):
        """Retourne la position de la case devant le joueur."""
        tile_size = 32  # Taille d'une case (à ajuster selon ta carte)

        direction_vectors = {
            "up": (0, -tile_size),
            "down": (0, tile_size),
            "left": (-tile_size, 0),
            "right": (tile_size, 0),
        }

        dx, dy = direction_vectors.get(self.direction, (0, 0))  # Récupère le déplacement
        front_x = self.rect.x + dx
        front_y = self.rect.y + dy

        return front_x // tile_size, front_y // tile_size  # Convertit en coordonnées de grille

    def place_item(self, tile_x, tile_y, all_blocks):
        """Pose l'objet que le joueur tient sur la case spécifiée."""
        if self.held_item:
            all_blocks.append(self.held_item)