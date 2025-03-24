import json

def load_elements(filename):
    """Charge les éléments depuis un fichier JSON."""
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    print("Données chargées :", data)
    return data["blocks"]