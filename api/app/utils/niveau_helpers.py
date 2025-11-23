"""
Helper functions for working with Niveau (Level) model with direct specialty relationship.
"""
from typing import Optional

def get_first_specialty(niveau):
    """
    Get the specialty associated with a level.
    This is a backward-compatible helper that now returns the direct specialty.
    
    Args:
        niveau: Niveau object with specialite included
        
    Returns:
        The Specialite object, or None if no specialty is associated
    """
    if not niveau:
        return None
    
    if hasattr(niveau, 'specialite'):
        return niveau.specialite
    
    return None


def get_all_specialties(niveau):
    """
    Get the specialty associated with a level.
    Returns a list for backward compatibility, but now contains only one specialty.
    
    Args:
        niveau: Niveau object with specialite included
        
    Returns:
        List containing the Specialite object (or empty list if none)
    """
    if not niveau:
        return []
    
    if hasattr(niveau, 'specialite') and niveau.specialite:
        return [niveau.specialite]
    
    return []


def has_specialty(niveau, specialty_id: str) -> bool:
    """
    Check if a level is associated with a specific specialty.
    
    Args:
        niveau: Niveau object with specialite included
        specialty_id: The ID of the specialty to check
        
    Returns:
        True if the level is associated with the specialty, False otherwise
    """
    if not niveau or not specialty_id:
        return False
    
    if hasattr(niveau, 'specialite') and niveau.specialite:
        return niveau.specialite.id == specialty_id
    
    if hasattr(niveau, 'id_specialite'):
        return niveau.id_specialite == specialty_id
    
    return False
