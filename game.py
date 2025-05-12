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
from Phase2.defense_game import DefenseGame
from music_manager import *
import pygame
import pyscroll
import pytmx


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()

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

        self.debug_collision = False  # Option pour afficher les zones de collision

        # Initialisation du gestionnaire de crafting automatique
        self.auto_craft_manager = AutoCraftManager(self)

        # Initialiser le gestionnaire de musique
        self.music_manager = MusicManager()
        self.music_manager.create_folder_structure()
        # Jouer la musique du laboratoire au démarrage
        self.music_manager.play_music("laboratory")

        # Chargement des données
        self.elements_data = load_elements("Data/elements.json")
        self.recipes_data = load_recipes("Data/recipes.json")
        self.potions_data = load_potions("Data/potion.json")
        self.enhancement_stones_data = load_enhancement_stones("Data/enhancement_stones.json")

        # Variables pour la pause et la victoire
        self.paused = False
        self.victory = False
        self.waves_completed = 0
        self.max_waves = 5  # Nombre de vagues à compléter pour gagner

        # Dictionnaire pour les cartes
        self.maps = {}
        self.current_map_name = "laboratoire"  # Carte par défaut

        # Dictionnaire pour stocker les éléments par carte
        self.map_elements = {
            "laboratoire": {
                "elements": pygame.sprite.LayeredUpdates(),
                "potions": pygame.sprite.LayeredUpdates(),
                "enhancement_stones": pygame.sprite.LayeredUpdates()
            },
            "cave": {
                "elements": pygame.sprite.LayeredUpdates(),
                "potions": pygame.sprite.LayeredUpdates(),
                "enhancement_stones": pygame.sprite.LayeredUpdates()
            }
        }

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

        # Inventaire du joueur (pour stocker des potions)
        self.player_inventory = []
        self.max_inventory_size = 10

        # Afficher un message de bienvenue
        self.ui.show_message("Bienvenue dans Pixel Alchemist ! Préparez vos potions !", 5.0)

    def detect_spawn_points(self):
        """Détecte les points de spawn dans les cartes TMX"""
        # Définir des valeurs par défaut pour tous les points de spawn
        # Cela garantit qu'ils existent même si rien n'est trouvé dans les cartes
        self.spawn_points = {
            "laboratoire": {
                "default": (220 + 128, 350),
                "from_trap": None,
                "from_ladder": (220 + 128, 350)
            },
            "cave": {
                "default": (129 + 128, 112),
                "from_trap": (129 + 128, 112),
                "from_ladder": None
            }
        }

        print("Points de spawn par défaut:", self.spawn_points)

        # Maintenant, cherchons les points définis dans les cartes pour remplacer les valeurs par défaut
        for map_name, map_data in self.maps.items():
            tmx_data = map_data["tmx_data"]

            # Pour chaque objet dans la carte
            for obj in tmx_data.objects:
                # Si c'est un point de spawn
                if obj.type == "Spawn":
                    self.spawn_points[map_name]["default"] = (obj.x, obj.y)
                    print(f"Point de spawn par défaut trouvé pour {map_name}: ({obj.x}, {obj.y})")
                elif obj.type == "trap_spawn":
                    self.spawn_points["cave"]["from_trap"] = (obj.x, obj.y)
                    print(f"Point de spawn après trappe trouvé: ({obj.x}, {obj.y})")
                elif obj.type == "ladder_spawn":
                    self.spawn_points["laboratoire"]["from_ladder"] = (obj.x, obj.y)
                    print(f"Point de spawn après échelle trouvé: ({obj.x}, {obj.y})")

        # Positionner le joueur au point de spawn par défaut de la carte initiale
        spawn = self.spawn_points[self.current_map_name]["default"]
        self.player.position[0] = spawn[0]
        self.player.position[1] = spawn[1]
        self.player.rect.topleft = self.player.position
        self.player.feet.midbottom = self.player.rect.midbottom


        print(f"Points de spawn finaux: {self.spawn_points}")
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

        # Utilisons directement la taille de l'écran pour le renderer sans zoom
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, (self.screen_width, self.screen_height))
        # Aucun zoom appliqué - rester à l'échelle 1.0
        map_layer.zoom = 1.0

        # Groupes pour les sprites de la carte
        group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=2)

        # Récupérer les zones de collision et autres zones spéciales
        walls = []
        craft_zones = []
        drop_zones = []
        potioncraft_zones = []
        creation_zones = []
        trap_zones = []
        end_craft_zones = []
        quest_zones = []
        map_zones = []

        for obj in tmx_data.objects:
            obj.x += 128
            if obj.type == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            if obj.type == "craft_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                zone = Zone(obj.x, obj.y, obj.id, obj.type)
                zone.game = self  # Assignation de la référence au jeu
                craft_zones.append(zone)
            if obj.type == "end_craft_zone":  # Nouvelle zone pour le résultat du craft
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                zone = Zone(obj.x, obj.y, obj.id, obj.type)
                zone.game = self  # Assignation de la référence au jeu
                end_craft_zones.append(zone)
            if obj.type == "drop_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                zone = Zone(obj.x, obj.y, obj.id, obj.type)
                zone.game = self  # Assignation de la référence au jeu
                drop_zones.append(zone)
            if obj.type == "potioncraft_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                zone = Zone(obj.x, obj.y, obj.id, obj.type)
                zone.game = self  # Assignation de la référence au jeu
                potioncraft_zones.append(zone)
            if obj.type == "zone_creation":
                if obj.name != "Terre":
                    walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                # Créer une zone de création avec son nom (Feu, Eau, Terre, Air)
                zone = Zone(obj.x, obj.y, obj.id, obj.type)
                zone.name = obj.name  # Ajouter le nom de l'élément à créer
                zone.game = self  # Assignation de la référence au jeu
                creation_zones.append(zone)
            if obj.type == "trap_zone" or obj.type == "ladder_zone":
                # Zones pour la transition entre cartes
                zone = Zone(obj.x, obj.y, obj.id, obj.type)
                zone.game = self  # Assignation de la référence au jeu
                trap_zones.append(zone)
            if obj.type == "quest_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                zone = Zone(obj.x, obj.y, obj.id, obj.type)
                if hasattr(obj, 'name'):
                    zone.name = obj.name
                zone.game = self  # Assignation de la référence au jeu
                quest_zones.append(zone)
            if obj.type == "map_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                zone = Zone(obj.x, obj.y, obj.id, obj.type)
                # Si la zone a un nom, l'ajouter
                if hasattr(obj, 'name'):
                    zone.name = obj.name
                zone.game = self  # Assignation de la référence au jeu
                map_zones.append(zone)

        # Ajout des bords de l'écran comme des collisions
        walls.append(pygame.Rect(-5, 0, 5, self.screen_height))
        walls.append(pygame.Rect(self.screen_width, 0, 5, self.screen_height))
        walls.append(pygame.Rect(0, -5, self.screen_width, 5))
        walls.append(pygame.Rect(0, self.screen_height, self.screen_width, 5))

        # Regrouper toutes les zones pour la détection
        zones = craft_zones + drop_zones + potioncraft_zones + creation_zones + trap_zones + end_craft_zones + quest_zones + map_zones

        # Stocker toutes les informations de la carte
        self.maps[map_name] = {
            "tmx_data": tmx_data,
            "map_data": map_data,
            "map_layer": map_layer,
            "group": group,
            "walls": walls,
            "zones": zones,
            "craft_zones": craft_zones,
            "end_craft_zones": end_craft_zones,  # Nouvelle propriété
            "drop_zones": drop_zones,
            "potioncraft_zones": potioncraft_zones,
            "creation_zones": creation_zones,
            "trap_zones": trap_zones,
            "quest_zones": quest_zones,
            "map_zones": map_zones
        }

    def setup_active_map(self):
        """Configure la carte active actuelle"""
        current_map = self.maps[self.current_map_name]

        # Mettre à jour les propriétés de la classe avec celles de la carte active
        self.walls = current_map["walls"]
        self.zones = current_map["zones"]
        self.craft_zones = current_map["craft_zones"]
        self.end_craft_zones = current_map["end_craft_zones"]
        self.drop_zones = current_map["drop_zones"]
        self.potioncraft_zones = current_map["potioncraft_zones"]
        self.creation_zones = current_map["creation_zones"]
        self.trap_zones = current_map["trap_zones"]
        self.quest_zones = current_map["quest_zones"]
        self.map_zones = current_map["map_zones"]

        # Configurer le groupe de dessin
        self.group = current_map["group"]

        # Stocker les éléments en fonction de la carte active
        if not hasattr(self, 'map_elements'):
            self.map_elements = {
                "laboratoire": {
                    "elements": pygame.sprite.LayeredUpdates(),
                    "potions": pygame.sprite.LayeredUpdates(),
                    "enhancement_stones": pygame.sprite.LayeredUpdates()
                },
                "cave": {
                    "elements": pygame.sprite.LayeredUpdates(),
                    "potions": pygame.sprite.LayeredUpdates(),
                    "enhancement_stones": pygame.sprite.LayeredUpdates()
                }
            }

        # Mettre à jour les groupes de sprites avec ceux de la carte active
        self.elements = self.map_elements[self.current_map_name]["elements"]
        self.potions = self.map_elements[self.current_map_name]["potions"]
        self.enhancement_stones = self.map_elements[self.current_map_name]["enhancement_stones"]

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
            spawn = self.spawn_points["cave"]["from_trap"]
            print(f"Téléportation vers la cave via trappe: {spawn}")
        elif self.transition_type == "ladder":
            # De la cave vers le laboratoire via l'échelle
            spawn = self.spawn_points["laboratoire"]["from_ladder"]
            print(f"Téléportation vers le laboratoire via échelle: {spawn}")
        else:
            # Point de spawn par défaut
            spawn = self.spawn_points[self.current_map_name]["default"]
            print(f"Téléportation vers le point par défaut: {spawn}")

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
                # Touche de pause (ESC)
                if event.key == pygame.K_ESCAPE:
                    self.toggle_pause()
                    continue

                # Si le jeu est en pause, ignorer les autres touches sauf ESC et H
                if self.paused:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_h:
                        self.show_help = not self.show_help
                    continue

                # Si l'écran de victoire est affiché
                if self.victory:
                    if event.key == pygame.K_SPACE:
                        # Réinitialiser le jeu pour une nouvelle partie
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                    continue

                # Touche C pour mélanger les potions
                if event.key == pygame.K_c:
                    # Vérifier si le joueur est devant la zone de mixage (zone 35)
                    front_zone = get_front_tile(self.player, self.zones)
                    if front_zone and front_zone.type == "potioncraft_zone" and front_zone.id == 35:
                        # Vérifier si un élément est placé sur la zone principale
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
                            self.ui.show_message("Mélange en cours...", 2.0)
                        else:
                            if not self.potion_craft_state["element"]:
                                self.ui.show_message("Placez d'abord un élément sur la zone centrale!", 2.0)
                            elif self.crafting_in_progress:
                                self.ui.show_message("Mélange déjà en cours...", 1.0)
                    else:
                        self.ui.show_message("Placez-vous devant la zone de mixage pour créer une potion!", 2.0)

                # Touche E pour les interactions
                if event.key == pygame.K_e:
                    # Vérifier s'il y a une zone devant le joueur
                    front_zone = get_front_tile(self.player, self.zones)
                    if front_zone:
                        # Traitement spécifique selon le type de zone

                        # Zone de lancement de la défense
                        if front_zone.type == "map_zone":
                            self.ui.show_message("Lancement de la phase de défense du laboratoire!", 2.0)
                            self.start_defense_phase()
                            continue

                        # Zones de transition entre cartes
                        elif front_zone.type == "trap_zone":
                            if self.current_map_name == "laboratoire":
                                self.change_map("cave", "trap")
                                continue

                        elif front_zone.type == "ladder_zone":
                            if self.current_map_name == "cave":
                                self.change_map("laboratoire", "ladder")
                                continue

                        # Zone du guide des potions
                        elif front_zone.type == "quest_zone":
                            self.show_potion_guide()
                            continue

                        # Zone de création d'élément
                        elif front_zone.type == "zone_creation":
                            if not self.player.held_item:
                                # Si la zone n'a pas d'objet dessus
                                if not front_zone.have_object:
                                    new_element = ElementFactory.create_base_element(self, front_zone.name)
                                    if new_element:
                                        self.player.held_item = new_element
                                        self.ui.show_message(f"Élément {front_zone.name} créé et récupéré!")
                                else:
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
                                            self.ui.show_message(f"Élément {obj.name} récupéré!")
                            continue

                        # Zone de craft de potion - Utiliser la fonction dédiée
                        elif front_zone.type == "potioncraft_zone":
                            self.handle_potion_craft_zone(front_zone)
                            continue

                        # Zone de résultat de craft - Utiliser la fonction dédiée
                        elif front_zone.type == "end_craft_zone":
                            # Vérifier si la zone contient réellement un objet
                            objects_on_zone = self.get_objects_on_zone(front_zone)

                            if objects_on_zone:
                                # Il y a un objet à récupérer
                                obj = objects_on_zone[0]
                                success = self.player.pick_element(obj)
                                if success:
                                    # Marquer explicitement la zone comme non occupée
                                    front_zone.have_object = False
                                    if isinstance(obj, Element):
                                        msg = f"Élément {obj.name} récupéré de la zone de résultat!"
                                    else:
                                        msg = "Objet récupéré de la zone de résultat!"
                                    self.ui.show_message(msg)
                            else:
                                # Si la zone est marquée comme occupée mais ne contient pas d'objet réel
                                if front_zone.have_object:
                                    print(
                                        "DEBUG: La zone était marquée comme occupée mais aucun objet n'a été trouvé. État corrigé.")
                                    front_zone.have_object = False

                                # Les zones end_craft_zone sont spéciales, elles ne permettent pas de déposer
                                self.ui.show_message("Aucun objet à récupérer sur cette zone.", 1.0)
                            continue

                        # Cas général - Dépôt et récupération d'objets
                        # Si on tient un objet, essayer de le déposer
                        if self.player.held_item:
                            # Vérifier si la zone est déjà occupée
                            if front_zone.have_object:
                                self.ui.show_message("Cette zone contient déjà un objet!", 1.0)
                                continue

                            # Tenter de déposer l'objet
                            success = self.player.drop_element(front_zone)
                            if success:
                                self.ui.show_message(f"Objet déposé")

                        # Si on ne tient pas d'objet, essayer d'en ramasser un
                        else:
                            game_objects = {
                                'elements': self.elements,
                                'potions': self.potions,
                                'stones': self.enhancement_stones
                            }

                            obj = get_element_on_tile(front_zone, game_objects, self.potion_craft_state)
                            if obj:
                                success = self.player.pick_element(obj)
                                if success:
                                    if isinstance(obj, Element):
                                        msg = f"Élément {obj.name} récupéré!"
                                    elif isinstance(obj, Potion):
                                        msg = f"Potion {obj.name} récupérée!"
                                    elif isinstance(obj, EnhancementStone):
                                        msg = f"Pierre d'amélioration récupérée!"
                                    else:
                                        msg = "Objet récupéré!"

                                    self.ui.show_message(msg)

                # Autres touches
                elif event.key == pygame.K_F1:
                    # Touche F1 pour activer/désactiver le débogage des collisions
                    self.debug_collision = not self.debug_collision
                    if self.debug_collision:
                        self.ui.show_message("Débogage des collisions activé", 2.0)
                    else:
                        self.ui.show_message("Débogage des collisions désactivé", 2.0)

                elif event.key == pygame.K_h:
                    # Touche pour afficher/masquer l'aide
                    self.show_help = not self.show_help

                elif event.key == pygame.K_F3:  # F3 pour afficher les informations sur les zones map_zone
                    self.print_map_zones()
                    self.ui.show_message("Informations sur les zones map_zone affichées dans la console", 2.0)

                elif event.key == pygame.K_F5:  # Utiliser F5 comme raccourci pour lancer la phase 2
                    self.ui.show_message("Lancement direct de la phase de défense!", 2.0)
                    self.start_defense_phase()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_c and self.crafting_in_progress:
                    # Si on relâche C, annuler le crafting
                    self.crafting_in_progress = False
                    self.crafting_timer = 0
                    self.animation_manager.remove_animation("potion_mixing")
                    self.ui.show_message("Mélange interrompu!", 1.0)

        # Vérifier si la touche C est maintenue enfoncée pour le crafting
        keys = pygame.key.get_pressed()
        if keys[pygame.K_c] and self.crafting_in_progress:
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

        if self.crafting_in_progress:
            self.crafting_timer += dt

            # Vérifier si le joueur est toujours devant la zone de mixage
            front_zone = get_front_tile(self.player, self.zones)
            if not front_zone or front_zone.type != "potioncraft_zone" or front_zone.id != 35:
                # Le joueur n'est plus devant la zone, annuler le crafting
                self.crafting_in_progress = False
                self.crafting_timer = 0
                self.animation_manager.remove_animation("potion_mixing")
                self.ui.show_message("Mélange interrompu! Vous avez quitté la zone.", 1.0)
                return

            # Vérifier si le temps requis est écoulé
            if self.crafting_timer >= self.crafting_time_required:
                self.crafting_in_progress = False
                self.crafting_timer = 0
                self.animation_manager.remove_animation("potion_mixing")

                # Appeler la fonction de création de potion
                success = self.create_potion_for_inventory()
                if not success:
                    self.ui.show_message("Échec de la création de la potion!", 2.0)

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

        # Vérifier les touches pressées et mettre à jour la direction du joueur
        keys = pygame.key.get_pressed()
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

        # Sauvegarder la position actuelle du joueur
        self.player.save_location()


        # Déplacement horizontal
        if self.player.velocity[0] != 0:
            # Calculer la nouvelle position horizontale
            new_x = self.player.position[0] + self.player.velocity[0] * self.player.speed

            # Mettre à jour temporairement la position horizontale
            old_x = self.player.position[0]
            self.player.position[0] = new_x
            self.player.rect.topleft = self.player.position
            self.player.feet.midbottom = self.player.rect.midbottom

            # Vérifier les collisions
            collision = False
            for wall in self.walls:
                if self.player.feet.colliderect(wall):
                    collision = True
                    break

            # Si collision, revenir à l'ancienne position horizontale
            if collision:
                self.player.position[0] = old_x
                self.player.rect.topleft = self.player.position
                self.player.feet.midbottom = self.player.rect.midbottom

        # Déplacement vertical (même principe)
        if self.player.velocity[1] != 0:
            # Calculer la nouvelle position verticale
            new_y = self.player.position[1] + self.player.velocity[1] * self.player.speed

            # Mettre à jour temporairement la position verticale
            old_y = self.player.position[1]
            self.player.position[1] = new_y
            self.player.rect.topleft = self.player.position
            self.player.feet.midbottom = self.player.rect.midbottom

            # Vérifier les collisions
            collision = False
            for wall in self.walls:
                if self.player.feet.colliderect(wall):
                    collision = True
                    break

            # Si collision, revenir à l'ancienne position verticale
            if collision:
                self.player.position[1] = old_y
                self.player.rect.topleft = self.player.position
                self.player.feet.midbottom = self.player.rect.midbottom

        # Finaliser la mise à jour du joueur
        self.player.update()

        # Mettre à jour les éléments transportés
        if self.player.held_item:
            self.player.held_item.update_position(self.player)

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
        craft_zones_used = []

        for zone in self.craft_zones:
            crafting_element = get_element_on_tile(zone, {'elements': self.elements}, None)
            if crafting_element:
                elements_craft.add(crafting_element)
                craft_zones_used.append(zone)

        recipe = check_block_craft(elements_craft, self.recipes_data)

        # S'il y a exactement 2 éléments et que la zone de résultat est libre
        if len(elements_craft) == 2 and (
                not self.end_craft_zones or not any(zone.have_object for zone in self.end_craft_zones)):
            recipe = check_block_craft(elements_craft, self.recipes_data)

            if recipe:
                print(f"Craft réussi : {recipe['result_name']}")

                # Supprimer les éléments utilisés
                for el in elements_craft:
                    self.elements.remove(el)

                # Libérer les zones de craft
                for zone in craft_zones_used:
                    zone.have_object = False

                # Trouver les données de l'élément résultant
                result_data = next(e for e in self.elements_data if e["id"] == recipe['result'])

                # Placer le nouvel élément dans la zone de résultat si elle existe
                if self.end_craft_zones:
                    result_zone = self.end_craft_zones[0]
                    new_element = Element(result_zone.rect.centerx, result_zone.rect.centery, result_data)
                    result_zone.have_object = True
                else:
                    # Fallback: utiliser le centre des zones de craft
                    center_x = sum(zone.rect.centerx for zone in craft_zones_used) // len(craft_zones_used)
                    center_y = sum(zone.rect.centery for zone in craft_zones_used) // len(craft_zones_used)
                    new_element = Element(center_x, center_y, result_data)

                self.elements.add(new_element)

                # Donner de l'XP pour le craft d'élément
                self.player.gain_experience(5)
                self.ui.show_message(f"Élément {recipe['result_name']} créé !")

    def display(self):
        # Effacer l'écran
        self.screen.fill((100, 100, 100))

        # Si nous sommes en transition, afficher uniquement l'animation de transition
        if self.transition_in_progress:
            progress = self.transition_timer / 1.0
            fade_value = int(255 * progress)
            fade_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, fade_value))
            self.screen.blit(fade_surface, (0, 0))

            # Afficher uniquement l'interface utilisateur pendant la transition
            self.ui.draw_temp_messages(self.screen)
            pygame.display.flip()
            return

        # Centrer la carte sur le joueur
        self.group.center(self.player.rect.center)

        # Dessiner la carte (sans le joueur pour l'instant)
        self.group.draw(self.screen)

        # Dessiner les éléments qui ne sont pas tenus par le joueur
        for element in self.elements:
            if not element.held_by_player:
                self.screen.blit(element.image, element.rect)

        for potion in self.potions:
            if not potion.held_by_player:
                self.screen.blit(potion.image, potion.rect)

        for stone in self.enhancement_stones:
            if not stone.held_by_player:
                self.screen.blit(stone.image, stone.rect)

        # Dessiner le joueur par-dessus les éléments au sol
        self.screen.blit(self.player.image, self.player.rect)

        # Dessiner les éléments tenus par le joueur par-dessus tout le reste
        if self.player.held_item:
            self.screen.blit(self.player.held_item.image, self.player.held_item.rect)

        # Dessiner les animations
        self.animation_manager.draw(self.screen)

        # Dessiner l'interface utilisateur avec l'inventaire
        self.ui.draw_player_info(self.screen, self.player, self.player_inventory)

        # Afficher les infobulles
        mouse_pos = pygame.mouse.get_pos()
        self.ui.draw_tooltip(self.screen, mouse_pos, self.elements, self.potions, self.enhancement_stones)

        # Afficher les messages temporaires
        self.ui.draw_temp_messages(self.screen)

        # REMARQUE : Le code d'affichage du timer a été supprimé ici

        # Afficher le nom de la carte actuelle
        map_text = f"Carte: {self.current_map_name.capitalize()}"
        map_font = pygame.font.SysFont('Arial', 20)
        map_surface = map_font.render(map_text, True, (255, 255, 255))
        self.screen.blit(map_surface, (10, self.screen_height - map_surface.get_height() - 10))

        # Afficher les contrôles de base
        controls_text = "E: Interagir | C: Mélanger | F1: Debug | H: Aide"
        controls_font = pygame.font.SysFont('Arial', 20)
        controls_surface = controls_font.render(controls_text, True, (200, 200, 200))
        self.screen.blit(controls_surface,
                         (self.screen_width - controls_surface.get_width() - 10, self.screen_height - 30))

        # DEBUG: Afficher la position du joueur et des éléments transportés
        if self.player.held_item and self.debug_collision:
            debug_text = f"Joueur: {self.player.rect.center}, Item: {self.player.held_item.rect.center}"
            debug_font = pygame.font.SysFont('Arial', 20)
            debug_surface = debug_font.render(debug_text, True, (255, 255, 0))
            self.screen.blit(debug_surface, (10, 40))

        # Afficher l'aide si demandé
        if self.show_help:
            self.draw_help()

        # Afficher les zones de collision si l'option de débogage est activée
        if self.debug_collision:
            self.draw_collision_debug()

        # Mettre à jour l'affichage
        pygame.display.flip()
    # Fonction d'écran de pause à ajouter à la classe Game
    def toggle_pause(self):
        """Active ou désactive la pause"""
        self.paused = not self.paused
        if self.paused:
            self.ui.show_message("Jeu en pause", 1.0)
        else:
            self.ui.show_message("Reprise du jeu", 1.0)

    def place_in_potion_craft_zone(self, zone):
        """Place l'objet tenu par le joueur dans la zone de craft de potion avec vérification renforcée"""
        if not self.player.held_item:
            print("DEBUG: Pas d'objet tenu par le joueur")
            return False

        # Vérifier si la zone est déjà occupée physiquement (pas juste le flag)
        objects_on_zone = self.get_objects_on_zone(zone)
        if objects_on_zone:
            print(f"DEBUG: Zone {zone.id} déjà occupée par un objet")
            return False

        # Vérifier si la zone est marquée comme occupée
        if zone.have_object:
            # Double vérification - si elle est marquée comme occupée mais ne contient pas d'objet
            # alors on corrige l'état
            if not objects_on_zone:
                print(f"DEBUG: Zone {zone.id} marquée comme occupée mais ne contient aucun objet. Correction...")
                zone.have_object = False
            else:
                print(f"DEBUG: Zone {zone.id} contient déjà un objet")
                return False

        # Vérifier si l'objet est déjà posé ailleurs (sur une autre zone)
        item = self.player.held_item
        for other_zone in self.potioncraft_zones:
            if other_zone != zone:
                other_objects = self.get_objects_on_zone(other_zone)
                for obj in other_objects:
                    if obj == item:
                        print(f"DEBUG: Cet objet est déjà posé sur la zone {other_zone.id}")
                        return False

        # Utiliser l'ID de la zone
        zone_id = zone.id
        print(f"DEBUG: Tentative de placement sur la zone ID: {zone_id}, type: {zone.type}")

        # Attribuer une fonction à chaque zone en fonction de son ID
        if zone_id == 35:  # Zone principale pour l'élément
            if isinstance(item, Element) and self.potion_craft_state["element"] is None:
                # Placer l'élément
                self.potion_craft_state["element"] = item
                item.held_by_player = False
                item.rect.center = zone.rect.center
                self.player.held_item = None
                zone.have_object = True
                print(f"DEBUG: Élément principal {item.name} placé sur la zone de crafting {zone_id}")
                return True
            else:
                if not isinstance(item, Element):
                    self.ui.show_message("Seuls les éléments peuvent être placés ici!", 1.5)
                else:
                    self.ui.show_message("Un élément est déjà présent!", 1.5)
                return False

        elif zone_id == 33:  # Zone pour la première pierre
            if isinstance(item, EnhancementStone) and self.potion_craft_state["stone1"] is None:
                self.potion_craft_state["stone1"] = item
                item.held_by_player = False
                item.rect.center = zone.rect.center
                self.player.held_item = None
                zone.have_object = True
                print(f"DEBUG: Pierre d'amélioration 1 ({item.stone_type}) placée sur zone {zone_id}")
                return True
            else:
                if not isinstance(item, EnhancementStone):
                    self.ui.show_message("Seules les pierres d'amélioration peuvent être placées ici!", 1.5)
                else:
                    self.ui.show_message("Une pierre est déjà présente!", 1.5)
                return False

        elif zone_id == 34:  # Zone pour la deuxième pierre
            if isinstance(item, EnhancementStone) and self.potion_craft_state["stone2"] is None:
                self.potion_craft_state["stone2"] = item
                item.held_by_player = False
                item.rect.center = zone.rect.center
                self.player.held_item = None
                zone.have_object = True
                print(f"DEBUG: Pierre d'amélioration 2 ({item.stone_type}) placée sur zone {zone_id}")
                return True
            else:
                if not isinstance(item, EnhancementStone):
                    self.ui.show_message("Seules les pierres d'amélioration peuvent être placées ici!", 1.5)
                else:
                    self.ui.show_message("Une pierre est déjà présente!", 1.5)
                return False

        # Si on arrive ici, la zone n'est pas reconnue ou l'objet n'est pas compatible
        print(f"DEBUG: Zone {zone_id} non reconnue ou objet incompatible")
        return False


    def get_objects_on_zone(self, zone):
        """Récupère tous les objets présents sur une zone avec une détection plus précise"""
        objects_on_zone = []

        # Définir un seuil de recouvrement (pourcentage minimum de l'objet sur la zone)
        overlap_threshold = 0.5

        # Vérifier chaque groupe d'objets
        for element in self.elements:
            if not element.held_by_player:
                # Calculer la zone de recouvrement
                overlap_rect = element.rect.clip(zone.rect)
                if overlap_rect.width > 0 and overlap_rect.height > 0:
                    # Calculer le pourcentage de recouvrement
                    element_area = element.rect.width * element.rect.height
                    overlap_area = overlap_rect.width * overlap_rect.height
                    if overlap_area / element_area >= overlap_threshold:
                        objects_on_zone.append(element)

        # Même logique pour les potions et les pierres
        for potion in self.potions:
            if not potion.held_by_player:
                overlap_rect = potion.rect.clip(zone.rect)
                if overlap_rect.width > 0 and overlap_rect.height > 0:
                    potion_area = potion.rect.width * potion.rect.height
                    overlap_area = overlap_rect.width * overlap_rect.height
                    if overlap_area / potion_area >= overlap_threshold:
                        objects_on_zone.append(potion)

        for stone in self.enhancement_stones:
            if not stone.held_by_player:
                overlap_rect = stone.rect.clip(zone.rect)
                if overlap_rect.width > 0 and overlap_rect.height > 0:
                    stone_area = stone.rect.width * stone.rect.height
                    overlap_area = overlap_rect.width * overlap_rect.height
                    if overlap_area / stone_area >= overlap_threshold:
                        objects_on_zone.append(stone)

        print(f"DEBUG: {len(objects_on_zone)} objets trouvés sur la zone {zone.id}")
        return objects_on_zone

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

    def create_potion_for_inventory(self):
        """Crée une potion et l'ajoute directement à l'inventaire du joueur"""
        if not self.potion_craft_state["element"]:
            print("DEBUG: Pas d'élément principal pour la potion")
            self.ui.show_message("Élément principal manquant pour créer la potion!", 2.0)
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
            print(f"DEBUG: Pas de potion possible avec l'élément {element_name}")
            self.ui.show_message(f"Impossible de créer une potion avec {element_name}!", 2.0)
            return False

        # Créer la potion (position temporaire)
        new_potion = Potion(0, 0, matching_potion, element_name)

        # Rapport des améliorations appliquées pour le message final
        enhancements = []

        # Appliquer les améliorations des pierres
        if self.potion_craft_state["stone1"]:
            stone_type = self.potion_craft_state["stone1"].stone_type
            new_potion.apply_enhancement(stone_type)
            self.enhancement_stones.remove(self.potion_craft_state["stone1"])
            # Libérer la zone de la pierre 1
            for zone in self.potioncraft_zones:
                if zone.id == 33:
                    zone.have_object = False
                    break
            self.potion_craft_state["stone1"] = None
            print("DEBUG: Pierre d'amélioration 1 appliquée et consommée")
            enhancements.append("puissance" if stone_type == "power" else "durée")

        if self.potion_craft_state["stone2"]:
            stone_type = self.potion_craft_state["stone2"].stone_type
            new_potion.apply_enhancement(stone_type)
            self.enhancement_stones.remove(self.potion_craft_state["stone2"])
            # Libérer la zone de la pierre 2
            for zone in self.potioncraft_zones:
                if zone.id == 34:
                    zone.have_object = False
                    break
            self.potion_craft_state["stone2"] = None
            print("DEBUG: Pierre d'amélioration 2 appliquée et consommée")
            enhancements.append("puissance" if stone_type == "power" else "durée")

        # Supprimer l'élément utilisé
        self.elements.remove(self.potion_craft_state["element"])
        # Libérer la zone de l'élément
        for zone in self.potioncraft_zones:
            if zone.id == 35:
                zone.have_object = False
                break
        self.potion_craft_state["element"] = None
        print("DEBUG: Élément principal consommé")

        # Ajouter la potion à l'inventaire du joueur
        if len(self.player_inventory) < self.max_inventory_size:
            self.player_inventory.append(new_potion)
            print(f"DEBUG: Potion {new_potion.name} ajoutée à l'inventaire")

            # Préparer le message de réussite
            message = f"Potion {new_potion.name} créée"
            if enhancements:
                if len(enhancements) == 1:
                    message += f" avec amélioration de {enhancements[0]}"
                else:
                    message += f" avec améliorations de {enhancements[0]} et {enhancements[1]}"
            message += " !"

            self.ui.show_message(message, 3.0)
        else:
            # Si l'inventaire est plein, créer la potion au sol près du joueur
            new_potion.rect.topleft = (self.player.rect.centerx + 20, self.player.rect.centery + 20)
            self.potions.add(new_potion)
            self.ui.show_message("Inventaire plein ! La potion a été déposée près de vous.", 2.0)
            print("DEBUG: Inventaire plein, potion déposée au sol")

        # Donner de l'XP au joueur
        self.player.craft_success(new_potion.category)

        print(f"DEBUG: Création réussie d'une potion {new_potion.name}!")
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

    def update_carried_items(self):
        """Met à jour la position des éléments transportés par le joueur"""
        if self.player.held_item:
            self.player.held_item.update_position(self.player)

    def handle_potioncraft_zone_pickup(self, zone):
        """Gère la récupération d'un objet sur une zone de craft de potion"""
        game_objects = {
            'elements': self.elements,
            'potions': self.potions,
            'stones': self.enhancement_stones
        }

        obj = get_element_on_tile(zone, game_objects, self.potion_craft_state)
        if obj:
            success = self.player.pick_element(obj)
            if success:
                zone.have_object = False

                # Message adapté au type d'objet récupéré
                if isinstance(obj, Element):
                    message = f"Élément {obj.name} récupéré!"
                elif isinstance(obj, EnhancementStone):
                    message = f"Pierre d'amélioration récupérée!"
                else:
                    message = "Objet récupéré!"

                self.ui.show_message(message, 1.5)
                return True

        return False

    def handle_potion_craft_zone(self, zone):
        """Gère l'interaction avec une zone de craft de potion de façon robuste"""
        zone_id = zone.id
        print(f"DEBUG: Interaction avec zone de craft de potion {zone_id}")

        # Vérifier si le joueur tient un objet
        if self.player.held_item:
            # Essayer de déposer l'objet
            success = self.place_in_potion_craft_zone(zone)
            if success:
                self.ui.show_message(f"Objet placé dans la zone de crafting {zone_id}", 1.5)
                return True
            else:
                self.ui.show_message("Impossible de placer cet objet ici!", 1.5)
                return False
        else:
            # Vérifier si la zone contient un objet à récupérer
            objects_on_zone = self.get_objects_on_zone(zone)

            if objects_on_zone:
                # Récupérer le premier objet trouvé
                obj = objects_on_zone[0]

                # Traiter les références dans potion_craft_state avant de récupérer l'objet
                if zone_id == 35 and self.potion_craft_state["element"] == obj:
                    print("DEBUG: Réinitialisation de l'élément principal")
                    self.potion_craft_state["element"] = None
                elif zone_id == 33 and self.potion_craft_state["stone1"] == obj:
                    print("DEBUG: Réinitialisation de la pierre 1")
                    self.potion_craft_state["stone1"] = None
                elif zone_id == 34 and self.potion_craft_state["stone2"] == obj:
                    print("DEBUG: Réinitialisation de la pierre 2")
                    self.potion_craft_state["stone2"] = None

                # Tenter de récupérer l'objet
                success = self.player.pick_element(obj)
                if success:
                    # Marquer explicitement la zone comme non occupée
                    zone.have_object = False

                    # Message adapté au type d'objet récupéré
                    if isinstance(obj, Element):
                        message = f"Élément {obj.name} récupéré!"
                    elif isinstance(obj, EnhancementStone):
                        message = f"Pierre d'amélioration récupérée!"
                    else:
                        message = "Objet récupéré!"

                    self.ui.show_message(message, 1.5)
                    return True
            else:
                # Si la zone est marquée comme occupée mais ne contient pas d'objet
                if zone.have_object:
                    print(f"DEBUG: Zone {zone.id} marquée comme occupée mais aucun objet trouvé. État corrigé.")
                    zone.have_object = False

                self.ui.show_message("Aucun objet à récupérer sur cette zone!", 1.5)
                return False

        return False

    def draw_potion_crafting_status(self):
        """Affiche l'état actuel du crafting de potions"""
        if not any([self.potion_craft_state["element"],
                    self.potion_craft_state["stone1"],
                    self.potion_craft_state["stone2"]]):
            return  # Ne rien afficher si aucun ingrédient n'est placé

        # Surface pour l'état du crafting
        status_width = 200
        status_height = 130
        status_x = 10
        status_y = 200  # En dessous de l'inventaire

        status_surface = pygame.Surface((status_width, status_height), pygame.SRCALPHA)
        status_surface.fill((0, 0, 0, 160))  # Fond semi-transparent

        # Titre
        font = pygame.font.SysFont('Arial', 16)
        title = font.render("État du crafting de potion", True, (255, 255, 255))
        status_surface.blit(title, (10, 5))

        # Élément principal
        y_pos = 30
        status_surface.blit(font.render("Élément:", True, (220, 220, 220)), (10, y_pos))
        if self.potion_craft_state["element"]:
            element_name = self.potion_craft_state["element"].name
            element_text = font.render(element_name, True, (100, 255, 100))
            status_surface.blit(element_text, (100, y_pos))
        else:
            status_surface.blit(font.render("Non placé", True, (255, 100, 100)), (100, y_pos))

        # Pierre 1
        y_pos += 25
        status_surface.blit(font.render("Pierre 1:", True, (220, 220, 220)), (10, y_pos))
        if self.potion_craft_state["stone1"]:
            stone_type = "Puissance" if self.potion_craft_state["stone1"].stone_type == "power" else "Durée"
            stone_text = font.render(stone_type, True, (100, 255, 100))
            status_surface.blit(stone_text, (100, y_pos))
        else:
            status_surface.blit(font.render("Non placée", True, (200, 200, 200)), (100, y_pos))

        # Pierre 2
        y_pos += 25
        status_surface.blit(font.render("Pierre 2:", True, (220, 220, 220)), (10, y_pos))
        if self.potion_craft_state["stone2"]:
            stone_type = "Puissance" if self.potion_craft_state["stone2"].stone_type == "power" else "Durée"
            stone_text = font.render(stone_type, True, (100, 255, 100))
            status_surface.blit(stone_text, (100, y_pos))
        else:
            status_surface.blit(font.render("Non placée", True, (200, 200, 200)), (100, y_pos))

        # Instructions
        y_pos += 30
        if self.potion_craft_state["element"]:
            instr = font.render("Appuyez sur C pour mélanger", True, (255, 255, 100))
            status_surface.blit(instr, (10, y_pos))

        # Afficher sur l'écran
        self.screen.blit(status_surface, (status_x, status_y))
    def draw_mixing_progress(self):
        """Affiche une barre de progression pendant le mélange de la potion"""
        if not self.crafting_in_progress:
            return

        # Position et dimensions de la barre
        bar_width = 200
        bar_height = 20
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = self.screen_height - 50

        # Calculer la progression
        progress = min(1.0, self.crafting_timer / self.crafting_time_required)

        # Dessiner le fond de la barre
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Dessiner la barre de progression
        progress_width = int(bar_width * progress)
        pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, progress_width, bar_height))

        # Bordure de la barre
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)

        # Pourcentage de progression
        percent = int(progress * 100)
        font = pygame.font.SysFont('Arial', 16)
        text = font.render(f"Mélange: {percent}%", True, (255, 255, 255))
        text_x = bar_x + (bar_width - text.get_width()) // 2
        text_y = bar_y - 25
        self.screen.blit(text, (text_x, text_y))
    def show_potion_guide(self):
        """Affiche le guide des potions sous forme de fenêtre popup"""
        # Créer une surface pour le guide
        guide_width = 600
        guide_height = 400
        guide_surface = pygame.Surface((guide_width, guide_height), pygame.SRCALPHA)
        guide_surface.fill((20, 20, 50, 230))  # Fond bleu foncé semi-transparent

        # Titre
        title_font = pygame.font.SysFont('Arial', 28, bold=True)
        title_text = title_font.render("GUIDE DE CRÉATION DES POTIONS", True, (255, 255, 255))
        guide_surface.blit(title_text, (guide_width // 2 - title_text.get_width() // 2, 20))

        # Sous-titre
        subtitle_font = pygame.font.SysFont('Arial', 20, bold=True)
        subtitle_text = subtitle_font.render("Comment créer une potion efficace", True, (200, 200, 255))
        guide_surface.blit(subtitle_text, (guide_width // 2 - subtitle_text.get_width() // 2, 60))

        # Instructions
        instruction_font = pygame.font.SysFont('Arial', 18)
        instructions = [
            "1. Collectez les éléments de base (Feu, Eau, Terre, Air) dans la cave ou le laboratoire",
            "2. Combinez-les sur la table de craft pour créer des éléments avancés (Tier 2, 3, 4)",
            "3. Trouvez des pierres d'amélioration (rouges pour puissance, bleues pour durée)",
            "4. Dans le laboratoire, placez les ingrédients dans la zone de potions :",
            "   - Placez l'élément principal dans la zone supérieure gauche",
            "   - Placez jusqu'à deux pierres d'amélioration dans les zones inférieures",
            "5. Placez-vous devant le chaudron (zone centrale) et appuyez sur la touche C",
            "6. Attendez que la potion se prépare, puis récupérez-la dans votre inventaire",
            "",
            "Combinaisons populaires :",
            "• Feu + Terre = Lave (dégâts importants + flaque brûlante)",
            "• Eau + Terre = Boue (ralentit les ennemis)",
            "• Eau + Air = Brouillard (invisibilité temporaire)",
            "• Feu + Eau = Vapeur (dégâts de zone + désorientation)",
            "• Terre + Terre = Pierre (étourdit les ennemis)",
            "• Lave + Fumée = Cendres (réduit puissance d'attaque des ennemis)",
            "",
            "Les potions peuvent être utilisées pendant la phase de défense.",
            "N'hésitez pas à expérimenter avec différentes combinaisons!"
        ]

        y = 100
        for line in instructions:
            line_text = instruction_font.render(line, True, (255, 255, 255))
            guide_surface.blit(line_text, (30, y))
            y += 25

        # Dessiner un petit diagramme
        # Zone de craft de potions
        pygame.draw.rect(guide_surface, (100, 100, 100), (450, 150, 120, 120), 2)

        # Élément principal (zone supérieure gauche)
        pygame.draw.rect(guide_surface, (255, 100, 100), (460, 160, 40, 40))
        label = instruction_font.render("Élément", True, (255, 255, 255))
        guide_surface.blit(label, (450, 130))

        # Chaudron (zone supérieure droite)
        pygame.draw.circle(guide_surface, (100, 100, 255), (520, 180), 20)
        label = instruction_font.render("Mixage (C)", True, (255, 255, 255))
        guide_surface.blit(label, (490, 130))

        # Pierre 1 (zone inférieure gauche)
        pygame.draw.rect(guide_surface, (255, 0, 0), (460, 210, 40, 40))
        label = instruction_font.render("Pierre 1", True, (255, 255, 255))
        guide_surface.blit(label, (450, 250))

        # Pierre 2 (zone inférieure droite)
        pygame.draw.rect(guide_surface, (0, 0, 255), (520, 210, 40, 40))
        label = instruction_font.render("Pierre 2", True, (255, 255, 255))
        guide_surface.blit(label, (510, 250))

        # Message de fermeture
        close_text = instruction_font.render("Appuyez sur une touche pour fermer", True, (255, 200, 200))
        guide_surface.blit(close_text, (guide_width // 2 - close_text.get_width() // 2, guide_height - 40))

        # Afficher le guide sur l'écran
        guide_x = (self.screen_width - guide_width) // 2
        guide_y = (self.screen_height - guide_height) // 2
        self.screen.blit(guide_surface, (guide_x, guide_y))
        pygame.display.flip()

        # Attendre une entrée utilisateur pour fermer
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting_for_input = False
                elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    waiting_for_input = False

    def draw_pause_screen(self):
        """Affiche l'écran de pause"""
        # Créer une surface semi-transparente
        pause_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        pause_surface.fill((0, 0, 0, 150))  # Fond noir semi-transparent

        # Titre
        title_font = pygame.font.SysFont('Arial', 40, bold=True)
        title_text = title_font.render("PAUSE", True, (255, 255, 255))
        pause_surface.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 150))

        # Instructions
        instruction_font = pygame.font.SysFont('Arial', 24)
        instructions = [
            "Appuyez sur P pour reprendre le jeu",
            "Appuyez sur H pour l'aide",
            "Appuyez sur ESC pour quitter"
        ]

        y = 250
        for line in instructions:
            line_text = instruction_font.render(line, True, (255, 255, 255))
            pause_surface.blit(line_text, (self.screen_width // 2 - line_text.get_width() // 2, y))
            y += 40

        # Informations sur la progression
        progress_font = pygame.font.SysFont('Arial', 20)
        progress_text = progress_font.render(f"Vagues complétées: {self.waves_completed}/{self.max_waves}", True,
                                             (200, 200, 255))
        pause_surface.blit(progress_text, (self.screen_width // 2 - progress_text.get_width() // 2, 380))

        # Statistiques du joueur
        stats_text = progress_font.render(f"Niveau: {self.player.level} | XP: {self.player.experience}", True,
                                          (200, 255, 200))
        pause_surface.blit(stats_text, (self.screen_width // 2 - stats_text.get_width() // 2, 410))

        self.screen.blit(pause_surface, (0, 0))

    def draw_collision_debug(self):
        """Dessine les zones de collision pour le débogage"""
        # Dessiner les murs
        for wall in self.walls:
            pygame.draw.rect(self.screen, (255, 0, 0, 128), wall, 2)

        # Dessiner les pieds du joueur
        pygame.draw.rect(self.screen, (0, 255, 0, 128), self.player.feet, 2)

        # Dessiner les différentes zones
        for zone in self.zones:
            if zone.type == "craft_zone":
                color = (0, 0, 255, 128)  # Bleu pour les zones de craft
            elif zone.type == "end_craft_zone":
                color = (255, 165, 0, 128)  # Orange pour les zones de résultat de craft
            elif zone.type == "drop_zone":
                color = (255, 255, 0, 128)  # Jaune pour les zones de dépôt
            elif zone.type == "potioncraft_zone":
                color = (255, 0, 255, 128)  # Magenta pour les zones de craft de potions
            elif zone.type == "zone_creation":
                color = (0, 255, 255, 128)  # Cyan pour les zones de création
            elif zone.type in ["trap_zone", "ladder_zone"]:
                color = (255, 128, 0, 128)  # Orange pour les zones de transition
            elif zone.type == "quest_zone":
                color = (75, 0, 130, 128)   # Indigo pour les zones de quête
            else:
                color = (128, 128, 128, 128)  # Gris pour les autres zones

            pygame.draw.rect(self.screen, color, zone.rect, 2)

            # Afficher l'ID et l'état d'occupation
            if self.debug_collision:
                font = pygame.font.SysFont('Arial', 10)
                text = f"{zone.id}"
                if hasattr(zone, "have_object") and zone.have_object:
                    text += " ✓"
                text_surface = font.render(text, True, (255, 255, 255))
                self.screen.blit(text_surface, (zone.rect.x + 2, zone.rect.y + 2))

    def start_defense_phase(self):
        """Démarre la phase de défense (phase 2) et gère le redémarrage"""
        # Sauvegarder l'état actuel du jeu si nécessaire
        current_screen = self.screen.copy()

        self.music_manager.play_music("defense")

        while True:  # Boucle pour permettre de rejouer
            # Créer une instance de DefenseGame avec toutes les potions disponibles
            defense_potions = self.player_inventory.copy()  # Utiliser les potions de l'inventaire plutôt que les potions au sol
            defense_game = DefenseGame(self.screen, self.player, defense_potions)

            # Afficher un message de transition
            self.ui.show_message(
                f"Préparation de la défense du laboratoire (Vague {self.waves_completed + 1}/{self.max_waves})...", 2.0)
            self.display()  # Mettre à jour l'affichage pour voir le message
            pygame.time.delay(2000)  # Attendre 2 secondes pour la transition

            # Lancer la phase de défense
            result = defense_game.run()

            # Vérifier si le joueur veut recommencer
            if isinstance(result, tuple) and len(result) == 3 and result[0] == "restart":
                # Le joueur veut recommencer, extraire le score et la vague
                defense_score, defense_wave = result[1], result[2]

                # Donner de l'expérience au joueur en fonction du score
                self.player.gain_experience(defense_score // 10)

                # Afficher un message pour le redémarrage
                self.ui.show_message("Redémarrage de la défense du laboratoire...", 2.0)
                self.display()
                pygame.time.delay(1500)

                # La boucle continue, créant une nouvelle partie
                continue

            # Sinon, c'est une fin normale de la partie
            defense_score, defense_wave = result

            # Mettre à jour la progression du joueur
            self.player.gain_experience(defense_score // 10)
            self.player.score += defense_score
            self.waves_completed += 1

            # Vider l'inventaire de potions après les avoir utilisées
            self.player_inventory = []

            # Vérifier si le joueur a terminé toutes les vagues
            if self.waves_completed >= self.max_waves:
                # Le joueur a gagné !
                self.victory = True
                self.ui.show_message("Victoire ! Vous avez défendu le laboratoire avec succès !", 5.0)

                # Afficher l'écran de victoire et attendre l'entrée utilisateur
                self.display()  # Cela affichera l'écran de victoire
                return
            else:
                # Afficher les résultats après la défense
                self.ui.show_message(
                    f"Défense terminée ! Score: {defense_score}, Vague {self.waves_completed}/{self.max_waves} complétée",
                    3.0)
                self.music_manager.play_music("laboratory")

                # Réinitialiser le timer pour la phase 1
                self.phase_timer = 120  # 2 minutes pour préparer les potions

                # Rétablir l'affichage de la phase 1
                self.screen.blit(current_screen, (0, 0))
                self.display()  # Mettre à jour l'affichage une fois de plus

                # Sortir de la boucle, retour à la phase 1
                break

    def print_map_zones(self):
        """Affiche toutes les zones map_zone disponibles dans chaque carte"""
        print("\n=== ZONES MAP_ZONE DÉTECTÉES ===")

        for map_name, map_data in self.maps.items():
            print(f"\n--- Carte: {map_name} ---")

            # Vérifier si map_zones existe dans le dictionnaire
            if "map_zones" in map_data:
                map_zones = map_data["map_zones"]
                if map_zones:
                    print(f"Nombre de zones map_zone: {len(map_zones)}")
                    for i, zone in enumerate(map_zones):
                        zone_name = getattr(zone, 'name', 'Sans nom')
                        print(f"  {i + 1}. ID: {zone.id}, Position: ({zone.rect.x}, {zone.rect.y}), Nom: {zone_name}")
                else:
                    print("Aucune zone map_zone trouvée dans cette carte.")
            else:
                print("La clé 'map_zones' n'existe pas dans les données de cette carte.")

    def show_victory_screen(self):
        """Affiche l'écran de victoire finale"""
        # Créer une surface semi-transparente
        victory_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        victory_surface.fill((0, 50, 0, 180))  # Fond vert foncé semi-transparent

        # Titre
        title_font = pygame.font.SysFont('Arial', 50, bold=True)
        title_text = title_font.render("VICTOIRE !", True, (255, 255, 100))
        victory_surface.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 120))

        # Message de félicitations
        subtitle_font = pygame.font.SysFont('Arial', 28)
        subtitle_text = subtitle_font.render("Félicitations, vous avez défendu le laboratoire avec succès !", True,
                                             (255, 255, 255))
        victory_surface.blit(subtitle_text, (self.screen_width // 2 - subtitle_text.get_width() // 2, 180))

        # Statistiques finales
        stats_font = pygame.font.SysFont('Arial', 22)
        stats = [
            f"Vagues complétées: {self.max_waves}/{self.max_waves}",
            f"Niveau final: {self.player.level}",
            f"Expérience totale: {self.player.experience}",
            f"Potions créées: {self.player.potion_count}",
            f"Score total: {self.player.score}"
        ]

        y = 250
        for line in stats:
            line_text = stats_font.render(line, True, (200, 255, 200))
            victory_surface.blit(line_text, (self.screen_width // 2 - line_text.get_width() // 2, y))
            y += 35

        # Message de fin
        conclusion_font = pygame.font.SysFont('Arial', 24)
        conclusion_text = conclusion_font.render("Vous êtes devenu un véritable maître alchimiste !", True,
                                                 (255, 255, 150))
        victory_surface.blit(conclusion_text, (self.screen_width // 2 - conclusion_text.get_width() // 2, 400))

        # Options
        options_font = pygame.font.SysFont('Arial', 22)
        options = [
            "Appuyez sur ESPACE pour rejouer",
            "Appuyez sur ESC pour quitter"
        ]

        y = 470
        for line in options:
            line_text = options_font.render(line, True, (255, 255, 255))
            victory_surface.blit(line_text, (self.screen_width // 2 - line_text.get_width() // 2, y))
            y += 35

        self.screen.blit(victory_surface, (0, 0))

    def reset_game(self):
        """Réinitialise le jeu pour une nouvelle partie"""
        # Réinitialiser les variables de jeu
        self.victory = False
        self.waves_completed = 0
        self.phase = 1
        self.phase_timer = 120

        # Réinitialiser le joueur
        self.player.level = 1
        self.player.experience = 0
        self.player.score = 0
        self.player.potion_count = 0

        # Vider les inventaires
        self.player_inventory = []

        # Revenir à la musique du laboratoire
        self.music_manager.play_music("laboratory")

        # Réinitialiser les éléments et potions
        for map_name in self.map_elements:
            self.map_elements[map_name]["elements"].empty()
            self.map_elements[map_name]["potions"].empty()
            self.map_elements[map_name]["enhancement_stones"].empty()

        # Réinitialiser l'état des zones
        for map_name, map_data in self.maps.items():
            for zone in map_data["zones"]:
                zone.have_object = False

        # Réinitialiser l'état du crafting de potion
        self.potion_craft_state = {
            "element": None,
            "stone1": None,
            "stone2": None,
            "result": None
        }

        # Replacer le joueur au point de spawn initial
        self.current_map_name = "laboratoire"
        self.setup_active_map()
        spawn = self.spawn_points[self.current_map_name]["default"]
        self.player.position[0] = spawn[0]
        self.player.position[1] = spawn[1]
        self.player.rect.topleft = self.player.position
        self.player.feet.midbottom = self.player.rect.midbottom

        # Afficher un message de bienvenue
        self.ui.show_message("Nouvelle partie commencée ! Préparez vos potions !", 3.0)

    def run(self):
        while self.running:
            self.player.save_location()
            self.handling_events()
            self.update()
            self.display()
            self.clock.tick(60)