def check_block_craft(posed_elements, recipes):
    """
    posed_elements : liste des éléments posés sur la table de craft
    recipes : liste des recettes (chargées depuis recipes.json)
    """
    posed_ids = sorted([el.id for el in posed_elements])



    for recipe in recipes:
        if sorted(recipe["ingredients"]) == posed_ids:
            return recipe  # On retourne toute la recette
    return None