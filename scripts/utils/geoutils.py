# Sylvio Dos Reis 2026
# A collection of useful geographic functions

def bound_expansion(coord1, coord2):
    """Expands the two (lattitude, longitude) coordinate pairs to return 1 tuple of (north, east, south, west) bounds coordinate"""
    
    north = max(coord1[0], coord2[0])
    south = min(coord1[0], coord2[0])
    east = max(coord1[1], coord2[1])
    west = min(coord1[1], coord2[1])
    
    return (north, east, south, west)