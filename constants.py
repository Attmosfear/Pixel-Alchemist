# Taille native de la carte (dimension réelle en pixels)
NATIVE_WIDTH = 320
NATIVE_HEIGHT = 224

# Facteur d'échelle pour l'affichage
# À terme, cette valeur pourra être chargée depuis un fichier de configuration
# ou définie via une interface de paramètres
SCALE = 3

# Taille de la fenêtre affichée
WINDOW_WIDTH = NATIVE_WIDTH * SCALE
WINDOW_HEIGHT = NATIVE_HEIGHT * SCALE