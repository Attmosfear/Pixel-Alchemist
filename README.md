# Pixel-Alchemist

# 🧪 Présentation du jeu
Pixel Alchemist est un jeu hybride qui mélange alchimie et défense de tour. Le joueur incarne un alchimiste qui doit créer des potions pour défendre son laboratoire contre des vagues d'ennemis. Le jeu se divise en deux phases distinctes :

Phase 1 : Construction des potions (mode puzzle) - Collectez des éléments de base, combinez-les pour créer des éléments plus avancés, puis transformez-les en potions puissantes.
Phase 2 : Défense du laboratoire (mode action) - Utilisez les potions créées en phase 1 pour défendre votre laboratoire contre des vagues d'ennemis.

 # 🎮 Fonctionnalités principales
Phase de construction

Système de crafting d'éléments : combinez des éléments de base (Eau, Feu, Terre, Air) pour créer plus de 20 éléments avancés
Système de création de potions avec 21 potions différentes aux effets variés
Pierres d'amélioration pour augmenter la puissance ou la durée des potions
Exploration de deux zones : le laboratoire et la cave
Système de progression du joueur avec niveaux et expérience

Phase de défense

Système de lancer de potions basé sur la physique
Différents types d'ennemis (terrestres et volants)
Effets visuels pour les potions (explosions, flammes, brouillard, etc.)
Différentes vagues d'ennemis avec difficulté croissante
Système de score

# 🕹️ Contrôles

Flèches directionnelles : Déplacer le personnage
E : Interagir (ramasser/déposer/utiliser)
C : Mélanger les potions (quand devant la zone appropriée)
H : Afficher/masquer le menu d'aide
ESC : Pause/Quitter

# 📋 Prérequis

Python 3.6 ou supérieur
Pygame
PyTMX
Pyscroll

# 🔧 Installation et lancement

Clonez le dépôt :

bashgit clone https://github.com/votre-username/pixel-alchemist.git
cd pixel-alchemist

Installez les dépendances :

bashpip install pygame pytmx pyscroll

Lancez le jeu :

bashpython main.py

# 🧩 Structure du projet

Pixel-Alchemist/

├── Assets/                  # Ressources graphiques et sonores
│   ├── Art/                 # Images du jeu
│   │   ├── Buildings/       # Bâtiments
│   │   ├── Effects/         # Effets visuels
│   │   ├── Enemies/         # Ennemis
│   │   └── Items/           # Objets (éléments, potions, pierres)
│   ├── Map/                 # Fichiers de cartes TMX
│   └── Sound/               # Musiques et sons
├── Data/                    # Fichiers de données JSON
│   ├── elements.json        # Données des éléments
│   ├── enhancement_stones.json # Données des pierres d'amélioration
│   ├── potion.json          # Données des potions
│   └── recipes.json         # Recettes de craft
├── Phase1/                  # Code pour la phase de construction
│   ├── animations.py        # Système d'animations
│   ├── craft_manager.py     # Gestion du crafting
│   ├── data_loader.py       # Chargement des données JSON
│   ├── element_factory.py   # Création des éléments
│   ├── elements.py          # Classe des éléments
│   ├── enhancement_stones.py # Classe des pierres d'amélioration
│   ├── placement_manager.py # Gestion des zones et placements
│   ├── player.py            # Classe du joueur
│   ├── potions.py           # Classe des potions
│   └── ui_manager.py        # Interface utilisateur
├── Phase2/                  # Code pour la phase de défense
│   ├── create_effect_sprites.py # Création des sprites d'effets
│   ├── defense_game.py      # Classe principale de la phase 2
│   ├── effects.py           # Effets des potions
│   ├── enemy.py             # Classe des ennemis
│   ├── laboratory.py        # Classe du laboratoire à défendre
│   └── launcher.py          # Système de lancement des potions
├── constants.py             # Constantes globales
├── game.py                  # Classe principale du jeu
├── main.py                  # Point d'entrée du jeu
└── music_manager.py         # Gestion de la musique

# 🎮 Guide du jeu

### Création d'éléments

Collectez des éléments de base (Feu, Eau, Terre, Air) dans les zones de création
Placez deux éléments sur les zones de craft pour les combiner
Récupérez l'élément créé dans la zone de résultat

### Création de potions

Placez un élément dans la zone principale de crafting de potion
Optionnellement, ajoutez des pierres d'amélioration (rouge pour puissance, bleue pour durée)
Tenez-vous devant le chaudron et appuyez sur C pour mélanger
La potion est ajoutée à votre inventaire

### Défense du laboratoire

Utilisez les potions de votre inventaire pour défendre le laboratoire
Visez avec la souris et cliquez pour lancer les potions
Différentes potions ont différents effets (dégâts directs, ralentissement, effet de zone, etc.)
Survivez à 5 vagues d'ennemis pour gagner

### 🏆 Système de progression

Gagnez de l'expérience en créant des potions et en éliminant des ennemis

Montez de niveau pour augmenter votre vitesse et la taille de votre inventaire

Complétez des vagues d'ennemis pour débloquer de nouvelles recettes

### 🧪 Combinaisons populaires

Feu + Terre = Lave (dégâts importants + flaque brûlante)
Eau + Terre = Boue (ralentit les ennemis)
Eau + Air = Brouillard (invisibilité temporaire)
Feu + Eau = Vapeur (dégâts de zone + désorientation)
Terre + Terre = Pierre (étourdit les ennemis)

# 🛠️ Développement
Ce projet a été développé en utilisant Python et Pygame. Il s'agit d'un prototype jouable qui peut être étendu avec de nouvelles fonctionnalités. N'hésitez pas à contribuer au projet en soumettant des pull requests ou en signalant des bugs.


# 👥 Crédits

Développé par Malo DESCHAMPS - Romain VIDEAU - Florian BONNEFOY - Mehdi MEZIOU - Romain MALOT

Inspiré par des jeux comme Overcooked et Pokémon Emerald
Graphismes et sons de sources libres
