def can_place_object(tile_x, tile_y, valid_zones):
    """Vérifie si la case est une zone de dépôt ou de craft."""
    for zone in valid_zones:
        if zone.collidepoint(tile_x * 32, tile_y * 32):
            return True
    return False