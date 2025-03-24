import random
import pygame

pygame.init()

# Dimension de la fenêtre
largeur, hauteur = 1180, 676
screen2 = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption('Pixel Alchemist')

# Couleurs
blanc = (255, 255, 255)
rouge = (255, 0, 0)
bleu = (0, 0, 255)

class Ennemi:
    def __init__(self):
        self.x = 0  # Départ à gauche
        self.y = random.randint(100, hauteur - 100)
        self.rayon = 20
        self.vitesse = random.uniform(2, 5)

    def mouvement(self):
        self.x += self.vitesse  # Déplacement vers la droite

    def draw(self, surface):
        pygame.draw.circle(surface, rouge, (int(self.x), int(self.y)), self.rayon)

class Projectile:
    def __init__(self, x, y, puissance):
        self.pos_x = x
        self.pos_y = y
        self.rayon = 10
        self.vitesse_x = -puissance * 1.5  # Portée horizontale
        self.vitesse_y = -puissance * 0.5  # Hauteur atteignable
        self.en_vol = True

    def deplacer(self):
        if self.en_vol:
            self.pos_x += self.vitesse_x
            self.pos_y += self.vitesse_y
            self.vitesse_y += 0.5  # Gravité

            if self.pos_y > hauteur or self.pos_x < 0:
                self.en_vol = False

    def afficher(self, surface):
        pygame.draw.circle(surface, bleu, (int(self.pos_x), int(self.pos_y)), self.rayon)
