"""
Formatage des données pour Google Sheets
"""

from datetime import datetime
from typing import Dict, List


def format_job_for_sheet(job: Dict) -> List:
    """
    Formate une offre pour l'insertion dans Google Sheets

    Args:
        job: Dictionnaire de l'offre

    Returns:
        Liste des valeurs dans l'ordre des colonnes
    """
    # Structure des colonnes selon le brief:
    # A: date_added, B: source, C: title, D: company, E: location,
    # F: salary_min, G: salary_max, H: job_url, I: ml_score,
    # J: status, K: notes, L: description_short

    today = datetime.now().strftime('%Y-%m-%d')

    # Salaire - afficher "TBD" si absent
    salary_min = job.get('salary_min')
    salary_min_str = str(int(salary_min)) if salary_min else "TBD"

    salary_max = job.get('salary_max')
    salary_max_str = str(int(salary_max)) if salary_max else ""

    # Description courte (premiers 200 caractères)
    description = job.get('description', '')
    description_short = description[:200] + '...' if len(description) > 200 else description

    return [
        today,                              # A: date_added
        job.get('source', 'N/A'),          # B: source
        job.get('title', 'N/A'),           # C: title
        job.get('company', 'N/A'),         # D: company
        job.get('location', 'N/A'),        # E: location
        salary_min_str,                     # F: salary_min
        salary_max_str,                     # G: salary_max
        job.get('job_url', ''),            # H: job_url
        job.get('ml_score', 0),            # I: ml_score
        '',                                 # J: status (vide par défaut)
        '',                                 # K: notes (vide)
        description_short,                  # L: description_short
    ]


def get_header_row() -> List[str]:
    """
    Retourne la ligne d'en-tête pour Google Sheets

    Returns:
        Liste des noms de colonnes
    """
    return [
        'date_added',
        'source',
        'title',
        'company',
        'location',
        'salary_min',
        'salary_max',
        'job_url',
        'ml_score',
        'status',
        'notes',
        'description_short',
    ]
