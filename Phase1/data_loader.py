import json

def load_elements(filename):
    """Charge les éléments depuis un fichier JSON."""
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    print("Données brutes chargées :", data)  # Vérification
    elements = data.get("blocks", [])  # On s'assure de récupérer une liste

    if not isinstance(elements, list):
        raise TypeError(f"Erreur : 'blocks' doit être une liste, reçu {type(elements)} : {elements}")

    return elements