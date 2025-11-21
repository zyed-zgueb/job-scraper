"""
Gestion de la configuration
"""

import os
from dotenv import load_dotenv
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Config:
    """Classe de configuration chargée depuis .env"""

    def __init__(self):
        # Charger les variables d'environnement
        load_dotenv()

        # Google Sheets
        self.google_sheet_id = os.getenv('GOOGLE_SHEET_ID', '')
        self.google_creds_json = os.getenv('GOOGLE_CREDS_JSON', './creds.json')

        # Email SMTP
        self.smtp_email = os.getenv('SMTP_EMAIL', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_recipient = os.getenv('SMTP_RECIPIENT', self.smtp_email)

        # Filtres
        self.min_salary = int(os.getenv('MIN_SALARY', '50000'))
        self.locations = os.getenv('LOCATIONS', 'Nancy,Metz,Épinal,remote').split(',')
        self.ml_score_threshold = float(os.getenv('ML_SCORE_THRESHOLD', '65'))
        self.max_remote_distance_km = int(os.getenv('MAX_REMOTE_DISTANCE_KM', '100'))

        # Indeed API (optionnel)
        self.indeed_api_key = os.getenv('INDEED_API_KEY', '')

        # Comportement
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'

        # Validation
        self._validate()

    def _validate(self):
        """Valide la configuration"""
        errors = []

        if not self.google_sheet_id:
            errors.append("GOOGLE_SHEET_ID manquant")

        if not self.smtp_email:
            errors.append("SMTP_EMAIL manquant")

        if not self.smtp_password:
            errors.append("SMTP_PASSWORD manquant")

        if errors:
            error_msg = "Erreurs de configuration:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Log de la config (sans les secrets)
        logger.info("Configuration chargée:")
        logger.info(f"  Google Sheet ID: {self.google_sheet_id}")
        logger.info(f"  SMTP Email: {self.smtp_email}")
        logger.info(f"  Min Salary: {self.min_salary}€")
        logger.info(f"  Locations: {', '.join(self.locations)}")
        logger.info(f"  ML Score Threshold: {self.ml_score_threshold}")
        logger.info(f"  Dry Run: {self.dry_run}")
        logger.info(f"  Debug: {self.debug}")
