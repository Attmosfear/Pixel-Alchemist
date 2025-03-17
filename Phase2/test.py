from mainP2 import *
#Liste des ennemis
ennemis = [Ennemi() for _ in range(5)] #Création de 5 ennemis
running = True
temps = pygame.time.Clock()
background = pygame.image.load("Phase2\First_background_im.png")

while running:
    screen2.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for en in ennemis:
        en.mouvement()
        en.draw(screen2)

        if en.x > largeur:
            ennemis.remove(en)
            ennemis.append(en)

    pygame.display.flip()
    temps.tick(60)

pygame.quit()