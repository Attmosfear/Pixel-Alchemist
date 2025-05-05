import json

def load_elements(path):
    """Charge les éléments depuis un fichier JSON."""
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    print("Données brutes chargées :", data)  # Vérification
    elements = data.get("blocks", [])  # On s'assure de récupérer une liste

    if not isinstance(elements, list):
        raise TypeError(f"Erreur : 'blocks' doit être une liste, reçu {type(elements)} : {elements}")

    return elements

def load_recipes(path):
    """Charge les recettes depuis un fichier JSON séparé."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["recipes"]

def load_potion(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    potions = data["potions"]
    if not isinstance(potions, list):
        raise TypeError(f"Erreur : 'blocks' doit être une liste, reçu {type(potions)} : {potions}")
    return potions

