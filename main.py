import constants
import pygame
import os

# Import de notre classe Game mise à jour
from game import Game


def main():
    # S'assurer que tous les dossiers nécessaires existent
    required_dirs = [
        "Assets/Art/Items/Potions",
        "Assets/Art/Items/Stones"
    ]

    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)

    # Initialiser Pygame
    pygame.init()
    pygame.display.set_caption("Pixel-Alchemist")

    # Utiliser les dimensions de constants.py
    screen = pygame.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))

    # Créer et exécuter le jeu
    game = Game(screen)
    game.run()

    # Quitter proprement
    pygame.quit()


if __name__ == "__main__":
    main()