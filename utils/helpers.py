"""
Fonctions utilitaires diverses
"""

import re
from typing import Optional


def clean_text(text: str) -> str:
    """
    Nettoie un texte (HTML, espaces superflus, etc.)

    Args:
        text: Texte à nettoyer

    Returns:
        Texte nettoyé
    """
    if not text:
        return ""

    # Supprimer les balises HTML
    text = re.sub(r'<[^>]+>', '', text)

    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)

    # Supprimer les espaces insécables
    text = text.replace('\xa0', ' ')

    return text.strip()


def extract_number(text: str) -> Optional[int]:
    """
    Extrait un nombre d'un texte

    Args:
        text: Texte contenant potentiellement un nombre

    Returns:
        Nombre extrait ou None
    """
    if not text:
        return None

    # Chercher des nombres
    matches = re.findall(r'\d+', text.replace(' ', ''))
    if matches:
        return int(matches[0])

    return None


def is_remote_job(location: str) -> bool:
    """
    Détermine si une offre est en remote

    Args:
        location: Texte de localisation

    Returns:
        True si remote
    """
    if not location:
        return False

    remote_keywords = ['remote', 'télétravail', 'teletravail', 'à distance', 'home office']
    location_lower = location.lower()

    return any(keyword in location_lower for keyword in remote_keywords)
