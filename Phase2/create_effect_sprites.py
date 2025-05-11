import pygame
import os
import math
import random


def ensure_dirs():
    """Crée les dossiers nécessaires s'ils n'existent pas"""
    os.makedirs("Assets/Art/Effects", exist_ok=True)
    print("Dossier des effets créé.")


def create_explosion_frames():
    """Crée des sprites d'explosion"""
    size = 100
    frames = []
    for i in range(7):  # 7 frames d'animation
        scale = 0.3 + i * 0.1  # Commence petit et grossit
        surf = pygame.Surface((size, size), pygame.SRCALPHA)

        # Cercle principal qui grossit
        alpha = 255 - int(180 * (i / 6))  # Devient plus transparent
        color = (255, 100, 0)  # Couleur orange pour le feu

        pygame.draw.circle(surf, (*color, alpha),
                           (size // 2, size // 2),
                           int((size // 2) * scale))

        # Éclats qui s'éloignent du centre
        for _ in range(5 + i * 3):
            angle = random.uniform(0, 2 * math.pi)
            dist = (0.5 + i * 0.1) * (size // 2) * scale
            px = int(size // 2 + math.cos(angle) * dist)
            py = int(size // 2 + math.sin(angle) * dist)
            p_size = random.randint(3, 8)
            p_alpha = random.randint(100, 230)
            pygame.draw.circle(surf, (*color, p_alpha), (px, py), p_size)

        frames.append(surf)

        # Sauvegarder l'image
        pygame.image.save(surf, f"Assets/Art/Effects/explosion{i + 1}.png")

    print("Frames d'explosion créées.")
    return frames


def create_smoke_frames():
    """Crée des sprites de fumée"""
    size = 120
    frames = []

    for i in range(10):  # 10 frames d'animation
        rising = size * (i / 10)  # La fumée monte
        expand = 0.5 + i * 0.1  # La fumée s'étend

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        color = (200, 200, 200)  # Couleur grise pour la fumée

        # Nuage de base qui monte et s'étend
        for _ in range(8 + i):
            cloud_x = size // 2 + random.uniform(-20 * expand, 20 * expand)
            cloud_y = size - 20 - rising + random.uniform(-10, 10)
            cloud_size = (10 + i * 2) * random.uniform(0.7, 1.3)
            alpha = 200 - i * 15

            pygame.draw.circle(surf, (*color, alpha),
                               (int(cloud_x), int(cloud_y)),
                               int(cloud_size))

        frames.append(surf)

        # Sauvegarder l'image
        pygame.image.save(surf, f"Assets/Art/Effects/smoke{i + 1}.png")

    print("Frames de fumée créées.")
    return frames


def create_water_frames():
    """Crée des sprites d'éclaboussure d'eau"""
    size = 120
    frames = []

    for i in range(8):  # 8 frames d'animation
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        color = (0, 100, 255)  # Couleur bleue pour l'eau

        if i < 3:  # Début: éclaboussure vers le haut
            # Gouttelettes qui montent
            for _ in range(10 + i * 5):
                angle = random.uniform(-math.pi, 0)  # Vers le haut
                dist = 10 + i * 15
                px = size // 2 + math.cos(angle) * dist
                py = size // 2 + math.sin(angle) * dist
                p_size = random.randint(3, 7)
                alpha = 200 - i * 20

                pygame.draw.circle(surf, (*color, alpha), (int(px), int(py)), p_size)
        else:  # Fin: formation de flaque
            # Flaque centrale
            flaque_size = 20 + (i - 3) * 10
            pygame.draw.ellipse(surf, (*color, 150),
                                (size // 2 - flaque_size, size // 2 + 10,
                                 flaque_size * 2, flaque_size // 2))

            # Gouttelettes qui retombent
            for _ in range(15 - i):
                px = size // 2 + random.uniform(-flaque_size, flaque_size)
                py = size // 2 + random.uniform(-30, 20)
                p_size = random.randint(2, 5)
                alpha = 150 + random.randint(-40, 40)

                pygame.draw.circle(surf, (*color, alpha), (int(px), int(py)), p_size)

        frames.append(surf)

        # Sauvegarder l'image
        pygame.image.save(surf, f"Assets/Art/Effects/water{i + 1}.png")

    print("Frames d'eau créées.")
    return frames


def create_fire_puddle_frames():
    """Crée des sprites de flaque de feu"""
    size = 120
    frames = []

    for i in range(12):  # 12 frames pour animation cyclique
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        color = (255, 100, 0)  # Couleur orange pour le feu

        # Flaque de base (ellipse)
        pygame.draw.ellipse(surf, (*color, 100), (10, size // 2, size - 20, size // 3))

        # Ajouter des flammes qui dansent
        cycle = (i % 4)  # Cycle de 4 frames
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(10, size // 2 - 10)
            px = size // 2 + math.cos(angle) * dist
            py = size // 2 + math.sin(angle) * dist

            # Variations de hauteur selon le cycle
            height = 10 + (cycle + random.uniform(-1, 1)) * 5

            # Dessiner une flamme (triangle)
            pygame.draw.polygon(surf, (*color, 180), [
                (px - 5, py),
                (px + 5, py),
                (px, py - height)
            ])

        frames.append(surf)

        # Sauvegarder l'image
        pygame.image.save(surf, f"Assets/Art/Effects/fire_puddle{i + 1}.png")

    print("Frames de flaque de feu créées.")
    return frames


def create_mud_frames():
    """Crée des sprites de flaque de boue"""
    size = 140
    frames = []

    for i in range(6):  # 6 frames d'animation
        surf = pygame.Surface((size, size // 2), pygame.SRCALPHA)
        color = (139, 69, 19)  # Couleur marron pour la boue

        # Flaque de base (ellipse)
        alpha = 220
        pygame.draw.ellipse(surf, (*color, alpha), (0, 0, size, size // 2))

        # Texture de la boue (petites taches plus sombres)
        darker_color = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40))
        for _ in range(20):
            px = random.randint(10, size - 10)
            py = random.randint(5, size // 2 - 5)
            p_size = random.randint(3, 8)
            pygame.draw.circle(surf, (*darker_color, alpha), (px, py), p_size)

        # Ajouter quelques bulles
        for j in range(3):
            if random.random() > 0.3:  # 70% de chance d'avoir une bulle
                px = random.randint(20, size - 20)
                py = random.randint(10, size // 2 - 10)
                p_size = random.randint(4, 10)
                lighter_color = (min(255, color[0] + 20), min(255, color[1] + 20), min(255, color[2] + 20))
                pygame.draw.circle(surf, (*lighter_color, alpha - 40), (px, py), p_size)
                # Reflet sur la bulle
                pygame.draw.circle(surf, (255, 255, 255, 100), (px - p_size // 3, py - p_size // 3), p_size // 3)

        frames.append(surf)

        # Sauvegarder l'image
        pygame.image.save(surf, f"Assets/Art/Effects/mud{i + 1}.png")

    print("Frames de boue créées.")
    return frames


def create_tornado_frames():
    """Crée des sprites de tornade"""
    width, height = 80, 160
    frames = []

    for i in range(10):  # 10 frames pour l'animation de rotation
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        color = (200, 200, 200)  # Couleur grisâtre pour la tornade

        # Base plus large
        base_width = width * 0.8
        pygame.draw.ellipse(surf, (*color, 150), (width / 2 - base_width / 2, height - 30, base_width, 30))

        # Corps de la tornade qui tourne
        angle = i * 36  # 10 frames, 360 degrés
        points = []

        # Points du côté gauche (de bas en haut)
        for j in range(6):
            h_pct = j / 5  # 0 à 1 (bas vers haut)
            curr_width = base_width * (1 - h_pct * 0.7)  # Rétréci vers le haut

            # Décalage horizontal basé sur l'angle
            h_offset = math.sin(math.radians(angle + h_pct * 360)) * curr_width / 3

            x = width / 2 - curr_width / 2 + h_offset
            y = height - 30 - h_pct * (height - 40)
            points.append((x, y))

        # Points du côté droit (de haut en bas)
        for j in range(5, -1, -1):
            h_pct = j / 5  # 0 à 1 (bas vers haut)
            curr_width = base_width * (1 - h_pct * 0.7)  # Rétréci vers le haut

            # Décalage horizontal basé sur l'angle
            h_offset = math.sin(math.radians(angle + h_pct * 360)) * curr_width / 3

            x = width / 2 + curr_width / 2 + h_offset
            y = height - 30 - h_pct * (height - 40)
            points.append((x, y))

        # Dessiner le polygone tornade
        if len(points) > 2:
            pygame.draw.polygon(surf, (*color, 180), points)

            # Ajouter des débris qui tournent
            for _ in range(10):
                h_pct = random.random()  # Position verticale
                curr_width = base_width * (1 - h_pct * 0.7) * 0.8

                # Décalage horizontal basé sur l'angle
                h_offset = math.sin(math.radians(angle + h_pct * 360)) * curr_width / 2

                x = width / 2 + h_offset + random.uniform(-curr_width / 2, curr_width / 2)
                y = height - 30 - h_pct * (height - 40)
                size = random.randint(2, 5)

                pygame.draw.circle(surf, (*color, 220), (x, y), size)

        frames.append(surf)

        # Sauvegarder l'image
        pygame.image.save(surf, f"Assets/Art/Effects/tornado{i + 1}.png")

    print("Frames de tornade créées.")
    return frames


def create_crystal_frames():
    """Crée des sprites de cristal gelant"""
    size = 100
    frames = []

    for i in range(8):  # 8 frames pour l'animation
        phase = i / 7  # 0 à 1

        if i < 4:  # Phase de croissance
            growth = phase * 2  # 0 à 1 (croissance jusqu'à frame 3)
        else:  # Phase de scintillement
            growth = 1.0

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        color = (200, 220, 255)  # Couleur bleu clair pour le cristal

        # Dessiner le cristal
        center = (size // 2, size // 2)
        num_spikes = 8

        for j in range(num_spikes):
            angle = j * (360 / num_spikes) + (i % 4) * 5  # Légère rotation pour scintillement
            length1 = 10 + 30 * growth  # Longueur principale
            length2 = 5 + 15 * growth  # Longueur secondaire

            # Point central
            x0, y0 = center

            # Premier point du cristal
            x1 = x0 + math.cos(math.radians(angle)) * length1
            y1 = y0 + math.sin(math.radians(angle)) * length1

            # Points secondaires (pour avoir un cristal plus large)
            angle_off = 15
            x2 = x0 + math.cos(math.radians(angle + angle_off)) * length2
            y2 = y0 + math.sin(math.radians(angle + angle_off)) * length2
            x3 = x0 + math.cos(math.radians(angle - angle_off)) * length2
            y3 = y0 + math.sin(math.radians(angle - angle_off)) * length2

            # Dessiner le triangle du cristal
            points = [(x0, y0), (x2, y2), (x1, y1), (x3, y3)]

            # Couleur avec effet de scintillement
            if i >= 4:
                alpha = 200 + (i % 4) * 10
                brightness = 200 + (i % 4) * 15
                crystal_color = (min(255, brightness), min(255, brightness), 255, alpha)
            else:
                crystal_color = (*color, 220)

            pygame.draw.polygon(surf, crystal_color, points)

        frames.append(surf)

        # Sauvegarder l'image
        pygame.image.save(surf, f"Assets/Art/Effects/crystal{i + 1}.png")

    print("Frames de cristal créées.")
    return frames


def generate_all_effects():
    """Génère tous les effets visuels pour les potions"""
    print("Génération des effets visuels des potions...")

    # Créer le dossier des effets s'il n'existe pas
    ensure_dirs()

    # Initialiser Pygame (nécessaire pour générer des surfaces)
    if not pygame.get_init():
        pygame.init()

    # Générer tous les types d'effets
    create_explosion_frames()
    create_smoke_frames()
    create_water_frames()
    create_fire_puddle_frames()
    create_mud_frames()
    create_tornado_frames()
    create_crystal_frames()

    print("Tous les effets visuels ont été générés avec succès!")


if __name__ == "__main__":
    generate_all_effects()