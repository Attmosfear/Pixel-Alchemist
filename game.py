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

        # Chargement des données
        self.elements_data = load_elements("Data/elements.json")
        self.recipes_data = load_recipes("Data/recipes.json")
        self.potions_data = load_potions("Data/potion.json")
        self.enhancement_stones_data = load_enhancement_stones("Data/enhancement_stones.json")

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
        self.load_map("laboratoire", "Assets/Map/Main 1/Map Laboratoire.tmx")
        self.load_map("cave", "Assets/Map/Main 1/Map Cave.tmx")

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
                "default": (220, 350),
                "from_trap": None,
                "from_ladder": (220, 350)
            },
            "cave": {
                "default": (129, 112),
                "from_trap": (129, 112),
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
            if obj.type == "collision":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            if obj.type == "craft_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                craft_zones.append(Zone(obj.x, obj.y, obj.id, obj.type))
            if obj.type == "end_craft_zone":  # Nouvelle zone pour le résultat du craft
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                end_craft_zones.append(Zone(obj.x, obj.y, obj.id, obj.type))
            if obj.type == "drop_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                drop_zones.append(Zone(obj.x, obj.y, obj.id, obj.type))
            if obj.type == "potioncraft_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                potioncraft_zones.append(Zone(obj.x, obj.y, obj.id, obj.type))
            if obj.type == "zone_creation":
                if obj.name != "Terre":
                    walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                # Créer une zone de création avec son nom (Feu, Eau, Terre, Air)
                zone = Zone(obj.x, obj.y, obj.id, obj.type)
                zone.name = obj.name  # Ajouter le nom de l'élément à créer
                creation_zones.append(zone)
            if obj.type == "trap_zone" or obj.type == "ladder_zone":
                # Zones pour la transition entre cartes
                trap_zone = Zone(obj.x, obj.y, obj.id, obj.type)
                trap_zones.append(trap_zone)
            if obj.type == "quest_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                quest_zone = Zone(obj.x, obj.y, obj.id, obj.type)
                if hasattr(obj, 'name'):
                    quest_zone.name = obj.name
                quest_zones.append(quest_zone)
            if obj.type == "map_zone":
                walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
                map_zone = Zone(obj.x, obj.y, obj.id, obj.type)
                # Si la zone a un nom, l'ajouter
                if hasattr(obj, 'name'):
                    map_zone.name = obj.name
                map_zones.append(map_zone)

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
                if event.key == pygame.K_e:
                    # Vérifier s'il y a une zone devant le joueur
                    front_zone = get_front_tile(self.player, self.zones)
                    if front_zone:
                        if front_zone.type == "map_zone":
                            # Afficher un message clair indiquant le lancement de la phase 2
                            self.ui.show_message("Lancement de la phase de défense du laboratoire!", 2.0)
                            # Lancer la phase de défense
                            self.start_defense_phase()
                            continue
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

                        elif front_zone.type == "end_craft_zone":
                            # Si on tient un objet, on ne peut pas le déposer dans la zone de résultat
                            if self.player.held_item:
                                self.ui.show_message("Vous ne pouvez pas déposer d'objets dans la zone de résultat!",
                                                     1.0)
                            else:
                                # On vérifie s'il y a un objet à récupérer
                                game_objects = {
                                    'elements': self.elements,
                                    'potions': self.potions,
                                    'stones': self.enhancement_stones
                                }
                                obj = get_element_on_tile(front_zone, game_objects, None)
                                if obj:
                                    success = self.player.pick_element(obj)
                                    if success:
                                        front_zone.have_object = False
                                        if isinstance(obj, Element):
                                            msg = f"Élément {obj.name} récupéré de la zone de résultat!"
                                        else:
                                            msg = "Objet récupéré de la zone de résultat!"
                                        self.ui.show_message(msg)
                        elif front_zone.type == "quest_zone":
                            # Logique pour les zones de quête
                            quest_name = front_zone.name if hasattr(front_zone, 'name') else "inconnue"
                            self.ui.show_message(
                                f"Zone de quête '{quest_name}' ! Des missions seront bientôt disponibles.", 3.0)
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

                elif event.key == pygame.K_ESCAPE:
                    # Échap pour cacher l'aide ou quitter
                    if self.show_help:
                        self.show_help = False
                    else:
                        self.running = False

                elif event.key == pygame.K_F3:  # F3 pour afficher les informations sur les zones map_zone
                    self.print_map_zones()
                    self.ui.show_message("Informations sur les zones map_zone affichées dans la console", 2.0)
                    continue

                elif event.key == pygame.K_F5:  # Utiliser F5 comme raccourci pour lancer la phase 2
                    self.ui.show_message("Lancement direct de la phase de défense!", 2.0)
                    self.start_defense_phase()
                    continue



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

        if self.crafting_in_progress:
            self.crafting_timer += dt
            self.crafting_animation_frame = (self.crafting_animation_frame + 1) % 30  # Pour une animation simple

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
                success = self.create_potion_for_inventory()
                if success:
                    self.ui.show_message("Potion créée et ajoutée à votre inventaire!", 3.0)
                else:
                    self.ui.show_message("Impossible de créer une potion...", 3.0)

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

        # Afficher le timer de la phase
        minutes = int(self.phase_timer // 60)
        seconds = int(self.phase_timer % 60)
        timer_text = f"Phase {self.phase} - Temps restant: {minutes:02}:{seconds:02}"
        timer_font = pygame.font.SysFont('Arial', 20)
        timer_surface = timer_font.render(timer_text, True, (255, 255, 255))
        self.screen.blit(timer_surface, (self.screen_width - timer_surface.get_width() - 10, 10))

        # Afficher le nom de la carte actuelle
        map_text = f"Carte: {self.current_map_name.capitalize()}"
        map_surface = timer_font.render(map_text, True, (255, 255, 255))
        self.screen.blit(map_surface, (10, self.screen_height - map_surface.get_height() - 10))

        # Afficher les contrôles de base
        controls_text = "E: Interagir | C: Mélanger | F1: Debug | H: Aide"
        controls_surface = timer_font.render(controls_text, True, (200, 200, 200))
        self.screen.blit(controls_surface,
                         (self.screen_width - controls_surface.get_width() - 10, self.screen_height - 30))

        # DEBUG: Afficher la position du joueur et des éléments transportés
        if self.player.held_item and self.debug_collision:
            debug_text = f"Joueur: {self.player.rect.center}, Item: {self.player.held_item.rect.center}"
            debug_surface = timer_font.render(debug_text, True, (255, 255, 0))
            self.screen.blit(debug_surface, (10, 40))

        # Afficher l'aide si demandé
        if self.show_help:
            self.draw_help()

        # Afficher les zones de collision si l'option de débogage est activée
        if self.debug_collision:
            self.draw_collision_debug()

        # Mettre à jour l'affichage
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

    def create_potion_for_inventory(self):
        """Crée une potion et l'ajoute directement à l'inventaire du joueur"""
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

        # Créer la potion (position temporaire)
        new_potion = Potion(0, 0, matching_potion, element_name)

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

        # Ajouter la potion à l'inventaire du joueur
        if len(self.player_inventory) < self.max_inventory_size:
            self.player_inventory.append(new_potion)
        else:
            # Si l'inventaire est plein, ajouter la potion au groupe des potions pour qu'elle soit visible
            new_potion.rect.topleft = (random.randint(100, 400), random.randint(100, 300))
            self.potions.add(new_potion)
            self.ui.show_message("Inventaire plein ! La potion a été déposée par terre.", 2.0)

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

    def update_carried_items(self):
        """Met à jour la position des éléments transportés par le joueur"""
        if self.player.held_item:
            self.player.held_item.update_position(self.player)

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

        while True:  # Boucle pour permettre de rejouer
            # Créer une instance de DefenseGame avec toutes les potions disponibles
            defense_game = DefenseGame(self.screen, self.player, self.potions)

            # Afficher un message de transition
            self.ui.show_message("Préparation de la défense du laboratoire...", 2.0)
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

            # Donner de l'expérience au joueur en fonction du score
            self.player.gain_experience(defense_score // 10)

            # Afficher les résultats après la défense
            self.ui.show_message(f"Défense terminée ! Score: {defense_score}, Vagues: {defense_wave}", 3.0)

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

    def run(self):
        while self.running:
            self.player.save_location()
            self.handling_events()
            self.update()
            self.display()
            self.clock.tick(60)