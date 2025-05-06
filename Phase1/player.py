import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('Assets/Art/player.png').convert()
        self.image = self.get_image(0, 0)
        self.rect = self.image.get_rect()
        self.position = [x, y]
        self.speed = 2
        self.velocity = [0, 0]
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 12)
        self.old_position = self.position.copy()
        self.direction = 'DOWN'

        # Inventaire du joueur
        self.held_item = None  # L'élément, potion ou pierre actuellement tenu
        self.inventory = []  # Pour une future implémentation d'inventaire plus complet
        self.inventory_size = 5  # Taille maximale de l'inventaire
        self.potion_count = 0  # Nombre de potions créées (pour le score)

        # Statistiques du joueur
        self.level = 1
        self.experience = 0
        self.score = 0

    def save_location(self):
        self.old_position = self.position.copy()

    def get_image(self, x, y):
        """
        Recupere l'image du joueur dans la spritsheet associée au joueur
        :param x: Position horizontal de l'image du joueur
        :param y: Position vertical de l'image du joueur
        :return: l'image du joueur
        """
        image = pygame.Surface([25, 30])
        image.blit(self.sprite_sheet, (0, 0), (x, y, 16, 16))
        return image

    def move(self):
        """
        Modifie la position du joueur sur la carte
        :return: Aucun car modification dynamique
        """
        self.position[0] += self.velocity[0] * self.speed
        self.position[1] += self.velocity[1] * self.speed

    def move_back(self):
        """
        Sauvegarde la position du joueur pour qu'en cas de collision celui ci s'arrete
        :return: Modification dynamique
        """
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    """Gestion des objets"""

    def pick_element(self, item):
        """
        Permet au joueur de récupérer un élément, une potion ou une pierre
        :param item: l'objet à récupérer
        :return: Modification dynamique
        """
        if self.held_item is not None:
            print(f"Tu tiens déjà l'objet suivant : {self.held_item}")
            return False

        print(f"Objet récupéré: {item}")
        self.held_item = item
        item.held_by_player = True
        return True

    def drop_element(self, zone):
        """
        Permet au joueur de poser un élément
        :param zone: zone sur laquelle l'objet est posé
        :return: Modification dynamique
        """
        if self.held_item:
            print(f"Objet déposé : {self.held_item}")
            self.held_item.held_by_player = False
            self.held_item.rect.center = zone.rect.center
            self.held_item = None
            zone.have_object = True
            return True
        else:
            print("Aucun objet à déposer")
            return False

    def gain_experience(self, amount):
        """
        Ajoute de l'expérience au joueur et vérifie s'il monte de niveau
        :param amount: Quantité d'expérience à ajouter
        """
        self.experience += amount

        # Vérifier si le joueur passe au niveau suivant
        # Formule simple : 100 XP * niveau actuel pour monter de niveau
        xp_required = 100 * self.level

        if self.experience >= xp_required:
            self.level_up()

    def level_up(self):
        """
        Fait monter le joueur d'un niveau et applique les améliorations
        """
        self.level += 1
        self.experience = 0  # Reset de l'XP

        # Améliorations possibles
        self.speed += 0.2  # Légère augmentation de la vitesse
        self.inventory_size += 1  # Une place d'inventaire supplémentaire

        print(f"Niveau supérieur ! Vous êtes maintenant niveau {self.level}")

    def craft_success(self, potion_type):
        """
        Appelé quand le joueur réussit à créer une potion
        :param potion_type: Le type de potion créée
        """
        self.potion_count += 1

        # Gain d'XP basé sur le type de potion
        if potion_type == "Attaque":
            xp_gain = 20
        elif potion_type == "Défense":
            xp_gain = 15
        else:  # Statut
            xp_gain = 10

        self.gain_experience(xp_gain)
        self.score += 50 * self.level  # Score basé sur le niveau actuel

    def update(self):
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom