
import random
import pygame
pygame.init()

#Dimension fenêtre
largeur,hauteur = 1180 ,676
screen2 = pygame.display.set_mode((largeur,hauteur))
pygame.display.set_caption('Pixel Alchemist')

blanc = (255,255,255)
rouge = (255,0,0)

class Ennemi:
    def __init__(self):
        self.x = 0 #Pour commencer à gauche
        self.y = random.randint(100,hauteur-100) #Pour avoir une position aléatoire
        self.rayon = 20
        self.vitesse = random.uniform(2,5)


    def mouvement(self):
        self.x = self.x + self.vitesse


    def draw(self,surface):
        pygame.draw.circle(surface, rouge, (int(self.x), int(self.y)), self.rayon)





