import pygame


class UIManager:
    def __init__(self, screen_width, screen_height):
        """
        Initialise le gestionnaire d'interface utilisateur
        :param screen_width: Largeur de l'écran
        :param screen_height: Hauteur de l'écran
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Polices
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)

        # Couleurs
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (150, 150, 150)
        self.LIGHT_BLUE = (173, 216, 230)
        self.DARK_BLUE = (0, 0, 139)

        # Création des surfaces
        self.info_surface = pygame.Surface((200, 100))
        self.inventory_surface = pygame.Surface((200, 80))
        self.tooltip_surface = None
        self.tooltip_text = ""

        # Messages temporaires
        self.temp_messages = []  # Liste de tuples (message, timer)

    def update(self, dt):
        """
        Met à jour les éléments de l'interface
        :param dt: Delta temps
        """
        # Mise à jour des messages temporaires
        for i in range(len(self.temp_messages) - 1, -1, -1):
            message, timer = self.temp_messages[i]
            timer -= dt
            if timer <= 0:
                self.temp_messages.pop(i)
            else:
                self.temp_messages[i] = (message, timer)

    def show_message(self, message, duration=3.0):
        """
        Affiche un message temporaire à l'écran
        :param message: Texte à afficher
        :param duration: Durée d'affichage en secondes
        """
        self.temp_messages.append((message, duration))

    def draw_player_info(self, screen, player, player_inventory=[]):
        """
        Dessine les informations du joueur (niveau, XP) et son inventaire
        :param screen: Surface d'affichage
        :param player: Objet joueur
        :param player_inventory: Liste des objets dans l'inventaire du joueur
        """
        # Fond semi-transparent
        info_surface = pygame.Surface((200, 80), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 128))

        # Titre
        level_text = self.title_font.render(f"Niveau {player.level}", True, self.WHITE)
        info_surface.blit(level_text, (10, 10))

        # Expérience
        xp_required = 100 * player.level
        xp_text = self.font.render(f"XP: {player.experience}/{xp_required}", True, self.WHITE)
        info_surface.blit(xp_text, (10, 40))

        # Barre d'XP
        pygame.draw.rect(info_surface, self.GRAY, (10, 60, 180, 10))
        xp_percentage = min(1.0, player.experience / xp_required)
        pygame.draw.rect(info_surface, self.LIGHT_BLUE, (10, 60, int(180 * xp_percentage), 10))

        # Affichage sur l'écran
        screen.blit(info_surface, (10, 10))

        # Afficher l'inventaire du joueur
        if player_inventory:
            self.draw_inventory(screen, player_inventory)

    def draw_inventory(self, screen, player_inventory):
        """
        Dessine l'inventaire du joueur
        :param screen: Surface d'affichage
        :param player_inventory: Liste des objets dans l'inventaire du joueur
        """
        # Position et taille du panel d'inventaire
        panel_width = 280
        panel_height = 60
        panel_x = 10
        panel_y = 100

        # Créer une surface semi-transparente pour le panel
        inventory_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        inventory_surface.fill((0, 0, 0, 160))

        # Titre
        title_text = self.font.render("Inventaire:", True, self.WHITE)
        inventory_surface.blit(title_text, (10, 5))

        # Afficher les objets de l'inventaire
        item_size = 32
        item_spacing = 5
        item_y = 25

        for i, item in enumerate(player_inventory):
            # Limiter à 6 objets par ligne pour éviter les débordements
            if i >= 6:
                break

            item_x = 10 + i * (item_size + item_spacing)

            # Dessiner un fond pour l'objet
            pygame.draw.rect(inventory_surface, (100, 100, 100),
                             (item_x, item_y, item_size, item_size))

            # Essayer d'afficher l'image de l'objet
            try:
                if hasattr(item, 'image'):
                    # Redimensionner l'image si nécessaire
                    item_img = item.image
                    if item_img.get_width() != item_size or item_img.get_height() != item_size:
                        item_img = pygame.transform.scale(item_img, (item_size, item_size))
                    inventory_surface.blit(item_img, (item_x, item_y))
            except (AttributeError, pygame.error):
                # Fallback si pas d'image : dessiner un rectangle coloré
                if isinstance(item, Potion):
                    if item.category == "Attaque":
                        color = (255, 0, 0)  # Rouge
                    elif item.category == "Défense":
                        color = (0, 0, 255)  # Bleu
                    else:
                        color = (0, 255, 0)  # Vert
                else:
                    color = (200, 200, 0)  # Jaune par défaut

                pygame.draw.rect(inventory_surface, color,
                                 (item_x + 4, item_y + 4, item_size - 8, item_size - 8))

        # Afficher le nombre total d'objets dans l'inventaire
        count_text = self.font.render(f"{len(player_inventory)}", True, self.WHITE)
        inventory_surface.blit(count_text, (panel_width - 30, 5))

        # Afficher sur l'écran
        screen.blit(inventory_surface, (panel_x, panel_y))

    def draw_inventory(self, screen, player):
        """
        Dessine l'inventaire du joueur
        :param screen: Surface d'affichage
        :param player: Objet joueur
        """
        # Ce sera pour une future implémentation d'inventaire plus complet
        pass

    def draw_potion_info(self, screen, potion, x, y):
        """
        Dessine les informations sur une potion
        :param screen: Surface d'affichage
        :param potion: Objet potion
        :param x, y: Position pour l'affichage
        """
        if not potion:
            return

        # Fond semi-transparent
        info_width = 180
        info_height = 100
        info_surface = pygame.Surface((info_width, info_height), pygame.SRCALPHA)
        info_surface.fill((0, 0, 0, 160))

        # Nom de la potion
        name_text = self.font.render(potion.name, True, self.WHITE)
        info_surface.blit(name_text, (10, 10))

        # Effet
        effect_text = self.font.render(potion.effect, True, self.LIGHT_BLUE)
        info_surface.blit(effect_text, (10, 35))

        # Puissance et durée
        power_text = self.font.render(f"Puissance: {potion.power}", True, self.WHITE)
        info_surface.blit(power_text, (10, 55))

        duration_text = self.font.render(f"Durée: {potion.duration}", True, self.WHITE)
        info_surface.blit(duration_text, (10, 75))

        # Affichage sur l'écran, en s'assurant qu'il reste visible
        x = min(x, screen.get_width() - info_width)
        y = min(y, screen.get_height() - info_height)
        screen.blit(info_surface, (x, y))

    def draw_tooltip(self, screen, mouse_pos, elements, potions, stones):
        """
        Affiche une infobulle quand le curseur est sur un objet
        :param screen: Surface d'affichage
        :param mouse_pos: Position de la souris
        :param elements, potions, stones: Groupes d'objets à vérifier
        """
        # Vérifier si la souris est sur un objet
        tooltip_text = None

        # Obtenir la position de la souris dans l'espace de jeu
        # Il n'y a plus de scale à prendre en compte, donc on utilise directement les coordonnées
        game_mouse_pos = mouse_pos

        # Vérifier les potions d'abord (priorité)
        for potion in potions:
            if potion.rect.collidepoint(game_mouse_pos):
                tooltip_text = f"{potion.name}: {potion.effect}"
                break

        # Ensuite les éléments
        if not tooltip_text:
            for element in elements:
                if element.rect.collidepoint(game_mouse_pos):
                    tooltip_text = f"{element.name} (Tier {element.tier})"
                    break

        # Enfin les pierres
        if not tooltip_text:
            for stone in stones:
                if stone.rect.collidepoint(game_mouse_pos):
                    if stone.stone_type == "power":
                        tooltip_text = "Pierre de Puissance"
                    else:
                        tooltip_text = "Pierre de Durée"
                    break

        # Si on a un texte, afficher la bulle
        if tooltip_text:
            font = self.font
            text_surface = font.render(tooltip_text, True, self.BLACK)
            width = text_surface.get_width() + 10
            height = text_surface.get_height() + 10

            tooltip = pygame.Surface((width, height))
            tooltip.fill(self.LIGHT_BLUE)
            pygame.draw.rect(tooltip, self.DARK_BLUE, (0, 0, width, height), 2)

            tooltip.blit(text_surface, (5, 5))

            # Position de la bulle près du curseur
            x = mouse_pos[0] + 15
            y = mouse_pos[1] + 15

            # S'assurer que la bulle reste visible
            if x + width > screen.get_width():
                x = screen.get_width() - width
            if y + height > screen.get_height():
                y = screen.get_height() - height

            screen.blit(tooltip, (x, y))

    def draw_temp_messages(self, screen):
        """
        Affiche les messages temporaires
        :param screen: Surface d'affichage
        """
        if not self.temp_messages:
            return

        # Position de départ
        y = screen.get_height() - 100

        for message, timer in self.temp_messages:
            # Calculer l'opacité basée sur le temps restant
            alpha = min(255, int(255 * (timer / 1.0)))

            text_surface = self.font.render(message, True, self.WHITE)
            text_width = text_surface.get_width() + 20

            back_surface = pygame.Surface((text_width, 30), pygame.SRCALPHA)
            back_surface.fill((0, 0, 0, int(alpha * 0.7)))

            back_surface.blit(text_surface, (10, 5))

            x = (screen.get_width() - text_width) // 2
            screen.blit(back_surface, (x, y))

            y -= 35  # Espacement vertical entre les messages