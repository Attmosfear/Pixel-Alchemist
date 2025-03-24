from mainP2 import *

# Initialisation
ennemis = []
projectiles = []
running = True
temps = pygame.time.Clock()
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (largeur, hauteur))

# Position de la jauge
position_jauge_y = hauteur // 2
vitesse_jauge = 40  # 2x plus rapide qu'avant
puissance = 0
en_trajectoire = False

# Variables pour les vagues
intervalle_vague = 5000  # 5 secondes
dernier_spawn = pygame.time.get_ticks()

while running:
    screen2.blit(background, (0, 0))
    temps_actuel = pygame.time.get_ticks()

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            en_trajectoire = True
            puissance = 0  # Réinitialisation de la puissance

        if event.type == pygame.MOUSEBUTTONUP:
            if en_trajectoire:
                origine_x, origine_y = largeur - 100, position_jauge_y
                nouveau_projectile = Projectile(origine_x, origine_y, puissance)
                projectiles.append(nouveau_projectile)
                en_trajectoire = False
                puissance = 0  # Réinitialisation après le tir

        # Déplacement de la jauge avec les flèches haut/bas
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                position_jauge_y = max(50, position_jauge_y - vitesse_jauge)  # Monte
            if event.key == pygame.K_DOWN:
                position_jauge_y = min(hauteur - 50, position_jauge_y + vitesse_jauge)  # Descend

    # Si le joueur maintient le clic, la puissance augmente
    if en_trajectoire and puissance < 30:
        puissance += 1

    # Gestion des vagues d'ennemis
    if temps_actuel - dernier_spawn > intervalle_vague:
        ennemis = [Ennemi() for _ in range(random.randint(3, 6))]
        dernier_spawn = temps_actuel

    # Mise à jour des ennemis
    for en in ennemis[:]:
        en.mouvement()
        en.draw(screen2)
        if en.x > largeur:
            ennemis.remove(en)

    # Mise à jour des projectiles
    for proj in projectiles[:]:
        proj.deplacer()
        proj.afficher(screen2)

        # Vérification des collisions avec les ennemis
        for en in ennemis:
            distance = ((proj.pos_x - en.x) ** 2 + (proj.pos_y - en.y) ** 2) ** 0.5
            if distance < proj.rayon + en.rayon:
                ennemis.remove(en)
                projectiles.remove(proj)
                break

    # Affichage de la jauge de puissance (se déplace verticalement)
    pygame.draw.rect(screen2, (255, 255, 255), (largeur - 120, position_jauge_y, 100, 10))
    pygame.draw.rect(screen2, (0, 255, 0), (largeur - 120, position_jauge_y, puissance * 3, 10))

    pygame.display.flip()
    temps.tick(60)

pygame.quit()