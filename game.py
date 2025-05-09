from Phase1.animations import *
from Phase1.craft_manager import *
from Phase1.data_loader import *
from Phase1.element_factory import ElementFactory
from Phase1.elements import Element
from Phase1.player import Player
from Phase1.placement_manager import *
from Phase1.potions import Potion
from Phase1.enhancement_stones import EnhancementStone
from Phase1.ui_manager import UIManager
from constants import *
import pygame
import pyscroll
import pytmx


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()

        # Nous n'utilisons plus la native_surface avec scaling
        # à la place, utilisons directement la taille de l'écran pour tout
        self.screen_width = WINDOW_WIDTH
        self.screen_height = WINDOW_HEIGHT

        self.recipe = None

        # Variable pour le crafting de potion
        self.crafting_in_progress = False
        self.crafting_timer = 0
        self.crafting_time_required = 2.0  # 2 secondes
        self.crafting_animation_frame = 0

        # Chargement de l'UI et du gestionnaire d'animations
        self.ui = UIManager(self.screen_width, self.screen_height)
        self.animation_manager = AnimationManager()

        # Initialisation du gestionnaire de crafting automatique
        self.auto_craft_manager = AutoCraftManager(self)

        # Chargement des données
        self.elements_data = load_elements("Data/elements.json")
        self.recipes_data = load_recipes("Data/recipes.json")
        self.potions_data = load_potions("Data/potion.json")
        self.enhancement_stones_data = load_enhancement_stones("Data/enhancement_stones.json")

        # Dictionnaire pour les cartes
        self.maps = {}
        self.current_map_name = "laboratoire"  # Carte par défaut

        # Charger les deux cartes
        self.load_map("laboratoire", "Assets/Map/Map Laboratoire.tmx")
        self.load_map("cave", "Assets/Map/Map Cave.tmx")

        # Points de spawn seront détectés depuis les cartes TMX
        self.spawn_points = {
            "laboratoire": {},
            "cave": {}
        }

        # Initialiser le joueur à une position temporaire, sera mis à jour après le chargement des spawns
        self.player = Player(0, 0)

        # Détecter les points de spawn dans les cartes TMX et initialiser le joueur
        self.detect_spawn_points()

        # Activer la carte courante
        self.setup_active_map()

        # Groupes pour les sprites
        self.elements = pygame.sprite.Group()
        self.potions = pygame.sprite.Group()
        self.enhancement_stones = pygame.sprite.Group()

        # État des zones de crafting de potions
        self.potion_craft_state = {
            "element": None,
            "stone1": None,
            "stone2": None,
            "result": None
        }

        # Variables pour la progression et le gameplay
        self.phase = 1  # 1 = Phase de crafting, 2 = Phase de défense
        self.phase_timer = 120  # 120 secondes (2 minutes) pour la phase 1
        self.last_time = pygame.time.get_ticks()
        self.show_help = False  # Pour afficher l'aide/tutoriel

        # Variables pour les transitions
        self.transition_in_progress = False
        self.transition_timer = 0
        self.transition_target = None
        self.transition_origin = None

        # Flag pour indiquer si le joueur vient d'être téléporté
        self.just_teleported = False
        self.teleport_cooldown = 0.5  # en secondes
        self.teleport_timer = 0

        # Afficher un message de bienvenue
        self.ui.show_message("Bienvenue dans Pixel Alchemist ! Préparez vos potions !", 5.0)

    def detect_spawn_points(self):
        """Détecte les points de spawn dans les cartes TMX"""
        for map_name, map_data in self.maps.items():
            tmx_data = map_data["tmx_data"]

            # Pour chaque objet dans la carte
            for obj in tmx_data.objects:
                # Si c'est un point de spawn
                if obj.type == "Spawn":
                    self.spawn_points[map_name]["default"] = (obj.x, obj.y)
                elif obj.type == "trap_spawn":
                    self.spawn_points[map_name]["from_trap"] = (obj.x, obj.y)
                elif obj.type == "ladder_spawn":
                    self.spawn_points[map_name]["from_ladder"] = (obj.x, obj.y)

        # Définir des valeurs par défaut au cas où certains points ne sont pas trouvés
        if "default" not in self.spawn_points["laboratoire"]:
            self.spawn_points["laboratoire"]["default"] = (220, 350)
        if "from_trap" not in self.spawn_points["cave"]:
            self.spawn_points["cave"]["from_trap"] = (129, 112)
        if "from_ladder" not in self.spawn_points["laboratoire"]:
            self.spawn_points["laboratoire"]["from_ladder"] = (220, 350)

        # Positionner le joueur au point de spawn par défaut de la carte initiale
        spawn = self.spawn_points[self.current_map_name]["default"]
        self.player.position[0] = spawn[0]
        self.player.position[1] = spawn[1]
        self.player.rect.topleft = self.player.position
        self.player.feet.midbottom = self.player.rect.midbottom

        print(f"Points de spawn détectés: {self.spawn_points}")

    def load_map(self, map_name, map_path):
        """Charge une carte depuis un fichier TMX et l'ajoute au dictionnaire des cartes"""
        tmx_data = pytmx.util_pygame.load_pygame(map_path)
        map_data = pyscroll.data.TiledMapData(tmx_data)

        # Utilisons directement la taille de l'écran pour le renderer au lieu du scaling
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, (self.screen_width, self.screen_height))
        map_layer.zoom = 2.0  # Ajuster le zoom directement via pyscroll

        # Groupes pour les sprites de la carte
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=2)

        # Récupérer les zones de collision et autres zones spéciales
        walls = []
        craft_zones = []
        drop_zones = []
        potioncraft_zones = []
        creation_zones = []
        trap_zones = []  # Nouvelles zones pour les pièges/trappes

        for obj in tmx_data.objects:
            if obj.type == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            if obj.type == "craft_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                craft_zones.append(Zone(obj.x, obj.y, obj.id, obj.type))
            if obj.type == "drop_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                drop_zones.append(Zone(obj.x, obj.y, obj.id, obj.type))
            if obj.type == "potioncraft_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                potioncraft_zones.append(Zone(obj.x, obj.y, obj.id, obj.type))
            if obj.type == "zone_creation":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                # Créer une zone de création avec son nom (Feu, Eau, Terre, Air)
                zone = Zone(obj.x, obj.y, obj.id, obj.type)
                zone.name = obj.name  # Ajouter le nom de l'élément à créer
                creation_zones.append(zone)
            if obj.type == "trap_zone" or obj.type == "ladder_zone":
                # Zones pour la transition entre cartes
                trap_zone = Zone(obj.x, obj.y, obj.id, obj.type)
                trap_zones.append(trap_zone)

        # Ajout des bords de l'écran comme des collisions (ajusté pour la taille réelle)
        walls.append(pygame.Rect(-5, 0, 5, self.screen_height))
        walls.append(pygame.Rect(self.screen_width, 0, 5, self.screen_height))
        walls.append(pygame.Rect(0, -5, self.screen_width, 5))
        walls.append(pygame.Rect(0, self.screen_height, self.screen_width, 5))

        # Regrouper toutes les zones pour la détection
        zones = craft_zones + drop_zones + potioncraft_zones + creation_zones + trap_zones

        # Stocker toutes les informations de la carte
        self.maps[map_name] = {
            "tmx_data": tmx_data,
            "map_data": map_data,
            "map_layer": map_layer,
            "group": group,
            "walls": walls,
            "zones": zones,
            "craft_zones": craft_zones,
            "drop_zones": drop_zones,
            "potioncraft_zones": potioncraft_zones,
            "creation_zones": creation_zones,
            "trap_zones": trap_zones
        }

    def setup_active_map(self):
        """Configure la carte active actuelle"""
        current_map = self.maps[self.current_map_name]

        # Mettre à jour les propriétés de la classe avec celles de la carte active
        self.walls = current_map["walls"]
        self.zones = current_map["zones"]
        self.craft_zones = current_map["craft_zones"]
        self.drop_zones = current_map["drop_zones"]
        self.potioncraft_zones = current_map["potioncraft_zones"]
        self.creation_zones = current_map["creation_zones"]
        self.trap_zones = current_map["trap_zones"]

        # Configurer le groupe de dessin
        self.group = current_map["group"]
        self.group.add(self.player)

    def change_map(self, target_map, transition_type):
        """Change la carte active et place le joueur au bon endroit"""
        if target_map not in self.maps:
            print(f"Erreur: Carte {target_map} non trouvée!")
            return

        # Sauvegarder l'origine pour l'animation de transition
        self.transition_in_progress = True
        self.transition_timer = 0
        self.transition_target = target_map
        self.transition_origin = self.current_map_name
        self.transition_type = transition_type

        # Message d'information pour le joueur
        self.ui.show_message(f"Transition vers {target_map}...", 2.0)

    def complete_map_change(self):
        """Termine le changement de carte après la transition"""
        # Mettre à jour la carte courante
        self.current_map_name = self.transition_target

        # Déplacer le joueur au bon point de spawn en fonction du type de transition
        if self.transition_type == "trap":
            # Du laboratoire vers la cave via la trappe
            spawn = self.spawn_points["cave"].get("from_trap", self.spawn_points["cave"]["default"])
        elif self.transition_type == "ladder":
            # De la cave vers le laboratoire via l'échelle
            spawn = self.spawn_points["laboratoire"].get("from_ladder", self.spawn_points["laboratoire"]["default"])
        else:
            # Point de spawn par défaut
            spawn = self.spawn_points[self.current_map_name]["default"]

        self.player.position[0] = spawn[0]
        self.player.position[1] = spawn[1]
        self.player.rect.topleft = self.player.position
        self.player.feet.midbottom = self.player.rect.midbottom

        # Configurer la nouvelle carte active
        self.setup_active_map()

        # Réinitialiser les variables de transition
        self.transition_in_progress = False
        self.just_teleported = True
        self.teleport_timer = 0

        # Message d'information pour le joueur
        self.ui.show_message(f"Bienvenue dans {self.current_map_name}!", 2.0)

    def handling_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                """Action"""
                if event.key == pygame.K_e:
                    # Vérifier s'il y a une zone devant le joueur
                    front_zone = get_front_tile(self.player, self.zones)
                    if front_zone:
                        # Si on est devant une trappe ou une échelle, changer de carte
                        if front_zone.type == "trap_zone":
                            # Transition du laboratoire vers la cave
                            if self.current_map_name == "laboratoire":
                                self.change_map("cave", "trap")

                        elif front_zone.type == "ladder_zone":
                            # Transition de la cave vers le laboratoire
                            if self.current_map_name == "cave":
                                self.change_map("laboratoire", "ladder")

                        # Si on est devant une zone de création d'élément
                        elif front_zone.type == "zone_creation":
                            if not self.player.held_item:
                                # Si la zone n'a pas d'objet dessus ou si l'objet a déjà été récupéré
                                if not front_zone.have_object:
                                    # Créer un nouvel élément de base et l'assigner directement au joueur
                                    new_element = ElementFactory.create_base_element(self, front_zone.name)
                                    if new_element:
                                        # L'élément est déjà assigné au joueur dans ElementFactory
                                        self.player.held_item = new_element
                                        self.ui.show_message(f"Élément {front_zone.name} créé et récupéré !")
                                else:
                                    # Il y a déjà un élément sur cette zone
                                    # Récupérer l'élément existant
                                    game_objects = {
                                        'elements': self.elements,
                                        'potions': self.potions,
                                        'stones': self.enhancement_stones
                                    }
                                    obj = get_element_on_tile(front_zone, game_objects, None)
                                    if obj:
                                        success = self.player.pick_element(obj)
                                        if success:
                                            self.ui.show_message(f"Élément {obj.name} récupéré !")
                            continue

                        # Si on est devant la zone de résultat et qu'on a un élément placé
                        if front_zone.type == "potioncraft_zone" and front_zone.id == 37:
                            if self.potion_craft_state["element"] is not None and not self.crafting_in_progress:
                                # Commencer le crafting
                                self.crafting_in_progress = True
                                self.crafting_timer = 0

                                # Démarrer l'animation
                                mixing_anim = PotionMixingAnimation(duration=self.crafting_time_required)
                                self.animation_manager.add_animation(
                                    "potion_mixing",
                                    mixing_anim,
                                    front_zone.rect.center
                                )
                                self.ui.show_message("Mélange en cours... Maintenez E", 2.0)
                                # Important : sortir du bloc après avoir commencé le crafting
                                # pour éviter d'exécuter le code de dépôt/récupération
                                continue

                        # Si on tient un objet, essayer de le déposer
                        if self.player.held_item:
                            # Essayons de déposer l'objet
                            if front_zone.type == "potioncraft_zone":
                                # Vérifier si la zone est déjà occupée
                                if front_zone.have_object:
                                    self.ui.show_message("Cette zone contient déjà un objet !", 1.0)
                                    continue

                                # Placer dans la zone de craft de potions
                                success = self.place_in_potion_craft_zone(front_zone)
                                if success:
                                    self.ui.show_message(f"Objet placé dans la zone de crafting de potions !")
                            else:
                                # Vérifier si la zone est déjà occupée
                                if front_zone.have_object:
                                    self.ui.show_message("Cette zone contient déjà un objet !", 1.0)
                                    continue

                                # Placer normalement
                                success = self.player.drop_element(front_zone)
                                if success:
                                    self.ui.show_message(f"Objet déposé")
                        else:
                            # On ne tient pas d'objet, essayer d'en ramasser un
                            game_objects = {
                                'elements': self.elements,
                                'potions': self.potions,
                                'stones': self.enhancement_stones
                            }

                            # Utiliser la fonction améliorée pour récupérer n'importe quel type d'objet
                            obj = get_element_on_tile(front_zone, game_objects, self.potion_craft_state)
                            if obj:
                                success = self.player.pick_element(obj)
                                if success:
                                    if isinstance(obj, Element):
                                        msg = f"Élément {obj.name} récupéré !"
                                    elif isinstance(obj, Potion):
                                        msg = f"Potion {obj.name} récupérée !"
                                    elif isinstance(obj, EnhancementStone):
                                        msg = f"Pierre d'amélioration récupérée !"
                                    else:
                                        msg = "Objet récupéré !"

                                    self.ui.show_message(msg)

                elif event.key == pygame.K_h:
                    # Touche pour afficher/masquer l'aide
                    self.show_help = not self.show_help

                elif event.key == pygame.K_ESCAPE:
                    # Échap pour cacher l'aide ou quitter
                    if self.show_help:
                        self.show_help = False
                    else:
                        self.running = False

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_e and self.crafting_in_progress:
                    # Si on relâche E, annuler le crafting
                    self.crafting_in_progress = False
                    self.crafting_timer = 0
                    self.animation_manager.remove_animation("potion_mixing")
                    self.ui.show_message("Mélange interrompu!", 1.0)

        # Vérifier si la touche E est maintenue enfoncée pour le crafting
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e] and self.crafting_in_progress:
            # Ici on ne fait rien, le timer est incrémenté dans update()
            pass
        else:
            """Mouvement"""
            # N'autorise le mouvement que si aucune transition n'est en cours
            if not self.transition_in_progress:
                if keys[pygame.K_LEFT]:
                    self.player.velocity[0] = -1
                    self.player.direction = 'LEFT'
                elif keys[pygame.K_RIGHT]:
                    self.player.velocity[0] = 1
                    self.player.direction = 'RIGHT'
                else:
                    self.player.velocity[0] = 0

                if keys[pygame.K_UP]:
                    self.player.velocity[1] = -1
                    self.player.direction = 'UP'
                elif keys[pygame.K_DOWN]:
                    self.player.velocity[1] = 1
                    self.player.direction = 'DOWN'
                else:
                    self.player.velocity[1] = 0

    def update(self):
        # Calculer le delta temps
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_time) / 1000.0  # Convertir en secondes
        self.last_time = current_time

        # Mettre à jour l'UI et les animations
        self.ui.update(dt)
        self.animation_manager.update(dt)

        # Gérer la transition de carte si nécessaire
        if self.transition_in_progress:
            self.transition_timer += dt
            # Attendre 1 seconde pour l'animation
            if self.transition_timer >= 1.0:
                self.complete_map_change()
            return  # Ne pas mettre à jour le reste pendant la transition

        # Gérer le cooldown après téléportation
        if self.just_teleported:
            self.teleport_timer += dt
            if self.teleport_timer >= self.teleport_cooldown:
                self.just_teleported = False

        # Mettre à jour le gestionnaire de crafting automatique
        self.auto_craft_manager.check_for_crafting()  # Vérifier s'il y a des éléments à crafter
        self.auto_craft_manager.update(dt)  # Mettre à jour le timer de crafting

        # Gérer le timer de crafting de potion
        if self.crafting_in_progress:
            self.crafting_timer += dt
            self.crafting_animation_frame = (self.crafting_animation_frame + 1) % 30  # Pour une animation simple

            # Vérifier si le joueur est toujours devant la zone de résultat
            front_zone = get_front_tile(self.player, self.zones)
            if not front_zone or front_zone.type != "potioncraft_zone" or front_zone.id != 37:
                # Le joueur n'est plus devant la zone, annuler le crafting
                self.crafting_in_progress = False
                self.crafting_timer = 0
                self.animation_manager.remove_animation("potion_mixing")
                self.ui.show_message("Mélange interrompu! Vous avez quitté la zone.", 1.0)
                return

            # Vérifier si la touche E est toujours enfoncée
            keys = pygame.key.get_pressed()
            if not keys[pygame.K_e]:
                # La touche E n'est plus enfoncée, annuler le crafting
                self.crafting_in_progress = False
                self.crafting_timer = 0
                self.animation_manager.remove_animation("potion_mixing")
                self.ui.show_message("Mélange interrompu! Vous avez relâché la touche E.", 1.0)
                return

            # Vérifier si le temps requis est écoulé
            if self.crafting_timer >= self.crafting_time_required:
                self.crafting_in_progress = False
                self.crafting_timer = 0
                self.animation_manager.remove_animation("potion_mixing")
                success = self.try_craft_potion()
                if success:
                    self.ui.show_message("Potion créée avec succès!", 3.0)
                else:
                    self.ui.show_message("Impossible de créer une potion...", 3.0)

        # Mettre à jour le timer de la phase
        if self.phase == 1:
            self.phase_timer -= dt
            if self.phase_timer <= 0:
                # Passer à la phase 2
                self.phase = 2
                self.ui.show_message("Fin de la phase de préparation ! Préparez-vous à défendre le laboratoire !", 5.0)
                # Ici, vous initialiseriez la phase 2, mais pour l'instant, on reset juste le timer
                self.phase_timer = 120
                self.phase = 1  # On reste en phase 1 pour le moment

        # Déplacement du joueur
        self.player.move()
        self.player.update()

        # Verification de collision
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()

        # Gestion des blocs en mouvement
        for element in self.elements:
            element.update_position(self.player)

        # Gestion des potions en mouvement
        for potion in self.potions:
            potion.update_position(self.player)

        # Gestion des pierres en mouvement
        for stone in self.enhancement_stones:
            stone.update_position(self.player)

        # Vérifier si le joueur est sur une zone de transition (seulement si pas en cooldown)
        if not self.just_teleported:
            for zone in self.trap_zones:
                if zone.rect.colliderect(self.player.rect):
                    # Si c'est une trappe, aller vers la cave
                    if zone.type == "trap_zone" and self.current_map_name == "laboratoire":
                        self.change_map("cave", "trap")
                        break
                    # Si c'est une échelle, remonter vers le laboratoire
                    elif zone.type == "ladder_zone" and self.current_map_name == "cave":
                        self.change_map("laboratoire", "ladder")
                        break

        # Gestion des crafts d'éléments
        elements_craft = pygame.sprite.Group()
        for zone in self.craft_zones:
            # Utiliser la version non-modifiée de get_element_on_tile pour les crafts d'éléments
            # car elle est spécifique à ce processus
            crafting_element = get_element_on_tile(zone, {'elements': self.elements}, None)
            if crafting_element:
                elements_craft.add(crafting_element)

        recipe = check_block_craft(elements_craft, self.recipes_data)

        if recipe and len(elements_craft) >= 2:  # Au moins 2 éléments pour un craft
            print(f"Craft réussi : {recipe['result_name']}")
            for el in elements_craft:
                self.elements.remove(el)

            result_data = next(e for e in self.elements_data if e["id"] == recipe['result'])

            position_crafted_element = self.craft_zones[0].rect
            new_element = Element(position_crafted_element.centerx, position_crafted_element.centery, result_data)
            self.elements.add(new_element)

            # Donner de l'XP pour le craft d'élément
            self.player.gain_experience(5)
            self.ui.show_message(f"Élément {recipe['result_name']} créé !")

    def display(self):
        # Dessiner le jeu de base sur l'écran directement (sans scaling)
        self.screen.fill((100, 100, 100))

        # Ne mettre à jour et dessiner que si on n'est pas en transition
        if not self.transition_in_progress:
            self.group.update()
            self.group.center(self.player.rect.center)
            self.group.draw(self.screen)

            # Dessiner tous les éléments de jeu
            self.elements.draw(self.screen)
            self.potions.draw(self.screen)
            self.enhancement_stones.draw(self.screen)

            # Dessiner les animations
            self.animation_manager.draw(self.screen)
        else:
            # Dessiner l'animation de transition
            progress = self.transition_timer / 1.0  # Durée totale de transition: 1 seconde
            fade_value = int(255 * progress)
            fade_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, fade_value))  # Noir avec alpha progressif
            self.screen.blit(fade_surface, (0, 0))

        # Dessiner l'interface utilisateur
        self.ui.draw_player_info(self.screen, self.player)

        # Afficher les infobulles si la souris est sur un objet
        mouse_pos = pygame.mouse.get_pos()
        # Utiliser directement les coordonnées de la souris, sans scaling
        self.ui.draw_tooltip(self.screen, mouse_pos, self.elements, self.potions, self.enhancement_stones)

        # Afficher les messages temporaires
        self.ui.draw_temp_messages(self.screen)

        # Afficher le timer de la phase
        minutes = int(self.phase_timer // 60)
        seconds = int(self.phase_timer % 60)
        timer_text = f"Phase {self.phase} - Temps restant: {minutes:02}:{seconds:02}"
        timer_font = pygame.font.SysFont('Arial', 20)
        timer_surface = timer_font.render(timer_text, True, (255, 255, 255))
        self.screen.blit(timer_surface, (self.screen_width - timer_surface.get_width() - 10, 10))

        # Afficher la carte actuelle
        map_text = f"Carte: {self.current_map_name.capitalize()}"
        map_surface = timer_font.render(map_text, True, (255, 255, 255))
        self.screen.blit(map_surface, (10, self.screen_height - map_surface.get_height() - 10))

        # Afficher l'aide si demandé
        if self.show_help:
            self.draw_help()

        pygame.display.flip()

    def place_in_potion_craft_zone(self, zone):
        """Place l'objet tenu par le joueur dans la zone de craft de potion"""
        if not self.player.held_item:
            print("DEBUG: Pas d'objet tenu par le joueur")
            return False

        # Vérifier si la zone est déjà occupée
        if zone.have_object:
            print("DEBUG: Cette zone contient déjà un objet")
            return False

        item = self.player.held_item

        # Utiliser l'ID de la zone au lieu de son index
        zone_id = zone.id
        print(f"DEBUG: Zone ID: {zone_id}, type: {zone.type}")

        # Attribuer une fonction à chaque zone en fonction de son ID
        # Ces IDs correspondent à ceux définis dans le fichier TMX

        if zone_id == 36:  # Élément principal (haut gauche)
            if isinstance(item, Element) and self.potion_craft_state["element"] is None:
                self.potion_craft_state["element"] = item
                item.held_by_player = False
                item.rect.center = zone.rect.center
                self.player.held_item = None
                zone.have_object = True  # Marquer la zone comme occupée
                return True

        elif zone_id == 38:  # Pierre 1 (bas gauche)
            if isinstance(item, EnhancementStone) and self.potion_craft_state["stone1"] is None:
                self.potion_craft_state["stone1"] = item
                item.held_by_player = False
                item.rect.center = zone.rect.center
                self.player.held_item = None
                zone.have_object = True  # Marquer la zone comme occupée
                return True

        elif zone_id == 39:  # Pierre 2 (bas droite)
            if isinstance(item, EnhancementStone) and self.potion_craft_state["stone2"] is None:
                self.potion_craft_state["stone2"] = item
                item.held_by_player = False
                item.rect.center = zone.rect.center
                self.player.held_item = None
                zone.have_object = True  # Marquer la zone comme occupée
                return True

        elif zone_id == 37:  # Résultat (haut droite)
            # Cette zone est réservée au résultat, on ne peut pas y déposer d'objets
            print("Cette zone est réservée au résultat de la potion")
            return False

        return False

    def try_craft_potion(self):
        """Essaye de créer une potion avec les éléments placés"""
        if not self.potion_craft_state["element"]:
            print("Pas d'élément principal pour la potion")
            return False

        # Récupérer le nom de l'élément principal
        element_name = self.potion_craft_state["element"].name
        print(f"DEBUG: Tentative de craft avec l'élément {element_name}")

        # Chercher une potion correspondante
        matching_potion = None
        for potion_data in self.potions_data:
            if element_name in potion_data["ingredients"]:
                matching_potion = potion_data
                print(f"DEBUG: Potion trouvée: {potion_data['name']}")
                break

        if not matching_potion:
            print(f"Pas de potion possible avec l'élément {element_name}")
            return False

        # Trouver la zone de résultat par ID
        result_zone = None
        for zone in self.potioncraft_zones:
            if zone.id == 37:  # ID de la zone de résultat
                result_zone = zone
                break

        if not result_zone:
            print("Zone de résultat non trouvée")
            return False

        # Marquer la zone comme libre avant de créer la potion
        result_zone.have_object = False

        new_potion = Potion(result_zone.rect.centerx, result_zone.rect.centery, matching_potion, element_name)

        # Appliquer les améliorations des pierres
        if self.potion_craft_state["stone1"]:
            new_potion.apply_enhancement(self.potion_craft_state["stone1"].stone_type)
            self.enhancement_stones.remove(self.potion_craft_state["stone1"])
            self.potion_craft_state["stone1"] = None

        if self.potion_craft_state["stone2"]:
            new_potion.apply_enhancement(self.potion_craft_state["stone2"].stone_type)
            self.enhancement_stones.remove(self.potion_craft_state["stone2"])
            self.potion_craft_state["stone2"] = None

        # Supprimer l'élément utilisé
        self.elements.remove(self.potion_craft_state["element"])
        self.potion_craft_state["element"] = None

        # Ajouter la potion aux potions disponibles
        self.potions.add(new_potion)
        self.potion_craft_state["result"] = new_potion

        # Marquer la zone de résultat comme occupée
        result_zone.have_object = True

        # Donner de l'XP au joueur
        self.player.craft_success(new_potion.category)

        print(f"Création réussie d'une potion {new_potion.name} !")
        return True

    def draw_help(self):
        """Affiche l'écran d'aide/tutoriel"""
        # Créer une surface semi-transparente
        help_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 180))

        # Titre
        title_font = pygame.font.SysFont('Arial', 30, bold=True)
        title_text = title_font.render("AIDE - PIXEL ALCHEMIST", True, (255, 255, 255))
        help_surface.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 50))

        # Instructions
        instructions = [
            "Contrôles:",
            "- Flèches directionnelles: Déplacer le personnage",
            "- E: Ramasser/Déposer un objet, Interagir avec les trappes/échelles",
            "- E (maintenu devant la zone de résultat): Créer une potion",
            "- H: Afficher/Masquer ce menu d'aide",
            "- ESC: Quitter le jeu",
            "",
            "Objectif Phase 1:",
            "- Collectez des éléments de base (Eau, Feu, Terre, Air)",
            "- Combinez-les sur la table de craft pour créer des éléments avancés",
            "- Utilisez ces éléments et des pierres d'amélioration pour créer des potions",
            "- Préparez-vous pour la phase de défense!",
            "",
            "Navigation:",
            "- Le jeu se compose de deux zones principales: le Laboratoire et la Cave",
            "- Utilisez la trappe (dans le laboratoire) pour descendre dans la cave",
            "- Utilisez l'échelle (dans la cave) pour remonter au laboratoire",
            "- Certains éléments ne se trouvent que dans certaines zones!",
            "",
            "Conseils:",
            "- Les potions ont des effets différents selon les éléments utilisés",
            "- Les pierres d'amélioration augmentent la puissance ou la durée des potions",
            "- Un seul objet peut être posé sur chaque case",
            "- Pour créer une potion, placez-vous devant la zone de résultat et maintenez E"
        ]

        font = pygame.font.SysFont('Arial', 20)
        y = 100
        for line in instructions:
            if line == "":
                y += 20
                continue

            text = font.render(line, True, (255, 255, 255))
            help_surface.blit(text, (self.screen_width // 2 - 250, y))
            y += 30

        # Message de fermeture
        close_text = font.render("Appuyez sur H pour fermer ce menu", True, (255, 200, 200))
        help_surface.blit(close_text, (self.screen_width // 2 - close_text.get_width() // 2, self.screen_height - 50))

        self.screen.blit(help_surface, (0, 0))

    def run(self):
        while self.running:
            self.player.save_location()
            self.handling_events()
            self.update()
            self.display()
            self.clock.tick(60)