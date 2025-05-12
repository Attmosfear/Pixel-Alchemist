import pygame
import os

# Classe pour gérer la musique du jeu
class MusicManager:
    def __init__(self):
        # Initialiser le module de son si ce n'est pas déjà fait
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Définir le volume par défaut
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)

        # Statut de la musique
        self.is_playing = False
        self.current_music = None

        # Chemins des fichiers musicaux (à créer ou ajouter)
        self.music_paths = {
            "menu": "Assets/Sound/Main 1/music main 1.mp3",
            "laboratory": "Assets/Sound/Main 1/music main 1.mp3",
            "cave": "Assets/Sound/Main 1/music main 1.mp3",
            "defense": "Assets/Sound/Main 2/music main 2.mp3",
            "victory": "Assets/Audio/victory_music.mp3"
        }

        # Faire en sorte que le code ne plante pas si les fichiers n'existent pas
        self.available_music = {}
        for key, path in self.music_paths.items():
            try:
                # Vérifier si le fichier existe
                if os.path.exists(path):
                    self.available_music[key] = path
            except:
                print(f"Musique {key} introuvable: {path}")

    def play_music(self, music_key, loops=-1):
        """
        Joue la musique spécifiée en boucle
        :param music_key: Clé de la musique à jouer (menu, laboratory, cave, defense, victory)
        :param loops: Nombre de répétitions (-1 pour infini)
        """
        # Vérifier si la musique existe
        if music_key not in self.available_music:
            print(f"Musique {music_key} non disponible")
            return False

        # Si c'est déjà la musique en cours, ne rien faire
        if self.current_music == music_key and self.is_playing:
            return True

        # Arrêter la musique actuelle si elle est en cours
        if self.is_playing:
            pygame.mixer.music.fadeout(500)  # Fade out de 500ms

        try:
            # Charger et jouer la nouvelle musique
            pygame.mixer.music.load(self.available_music[music_key])
            pygame.mixer.music.play(loops)
            self.current_music = music_key
            self.is_playing = True
            print(f"Musique '{music_key}' lancée")
            return True
        except Exception as e:
            print(f"Erreur lors du chargement de la musique: {e}")
            self.is_playing = False
            return False

    def stop_music(self, fadeout_ms=500):
        """Arrête la musique avec un fondu"""
        if self.is_playing:
            pygame.mixer.music.fadeout(fadeout_ms)
            self.is_playing = False
            print("Musique arrêtée")

    def pause_music(self):
        """Met en pause la musique"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            print("Musique en pause")

    def unpause_music(self):
        """Reprend la musique mise en pause"""
        pygame.mixer.music.unpause()
        self.is_playing = True
        print("Musique reprise")

    def set_volume(self, volume):
        """
        Définit le volume de la musique
        :param volume: Valeur entre 0.0 et 1.0
        """
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        print(f"Volume réglé à {self.volume}")

    def create_folder_structure(self):
        """Crée l'arborescence des dossiers pour la musique"""
        os.makedirs("Assets/Audio", exist_ok=True)
        print("Dossier Audio créé")
