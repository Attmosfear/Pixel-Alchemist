# Définir directement la taille de la fenêtre sans facteur d'échelle
# Nous n'utilisons plus SCALE, mais conservons les dimensions natives
# pour la compatibilité avec certaines fonctions de calcul

# Dimensions originales du jeu (utilisées pour les calculs)
NATIVE_WIDTH = 512  # Augmenté pour voir plus de la carte
NATIVE_HEIGHT = 448  # Augmenté pour voir plus de la carte

# Définir la fenêtre d'affichage avec les mêmes dimensions
# pyscroll s'occupera du zoom directement
WINDOW_WIDTH = NATIVE_WIDTH
WINDOW_HEIGHT = NATIVE_HEIGHT

# Nous gardons SCALE à 1 pour la compatibilité, mais ce n'est plus utilisé
# pour le scaling de la fenêtre
SCALE = 1