"""
Configuration du logging
"""

import logging
import sys
from datetime import datetime


def setup_logger(name: str) -> logging.Logger:
    """
    Configure et retourne un logger

    Args:
        name: Nom du logger (généralement __name__)

    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)

    # Éviter la duplication si déjà configuré
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler fichier (optionnel)
    try:
        log_filename = f"logs/job_scraper_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        # Si le dossier logs n'existe pas, continuer sans file handler
        pass

    return logger
