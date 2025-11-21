"""
API Google Sheets pour ajouter et gérer les offres
"""

import os
from typing import List, Dict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .formatter import format_job_for_sheet, get_header_row
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GoogleSheetsAPI:
    """Interface pour Google Sheets API"""

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, config):
        self.config = config
        self.sheet_id = config.google_sheet_id
        self.creds_file = config.google_creds_json

        logger.info("Initialisation de Google Sheets API...")
        self.service = self._authenticate()
        logger.info("✅ Authentification Google Sheets réussie")

    def _authenticate(self):
        """Authentification avec les credentials du service account"""
        try:
            if not os.path.exists(self.creds_file):
                raise FileNotFoundError(f"Fichier credentials non trouvé: {self.creds_file}")

            credentials = Credentials.from_service_account_file(
                self.creds_file,
                scopes=self.SCOPES
            )

            service = build('sheets', 'v4', credentials=credentials)
            return service

        except Exception as e:
            logger.error(f"Erreur d'authentification Google Sheets: {str(e)}")
            raise

    def append_jobs(self, jobs: List[Dict]) -> int:
        """
        Ajoute des offres au Google Sheet

        Args:
            jobs: Liste des offres à ajouter

        Returns:
            Nombre d'offres effectivement ajoutées
        """
        if not jobs:
            logger.info("Aucune offre à ajouter")
            return 0

        try:
            # Vérifier si le header existe, sinon le créer
            self._ensure_header_exists()

            # Récupérer les URLs existantes pour éviter les doublons
            existing_urls = self._get_existing_urls()
            logger.info(f"URLs déjà présentes dans le Sheet: {len(existing_urls)}")

            # Filtrer les nouvelles offres
            new_jobs = [job for job in jobs if job.get('job_url') not in existing_urls]
            logger.info(f"Nouvelles offres à ajouter: {len(new_jobs)}")

            if not new_jobs:
                logger.info("Aucune nouvelle offre (tous des doublons)")
                return 0

            # Formater les données
            rows = [format_job_for_sheet(job) for job in new_jobs]

            # Ajouter au Sheet
            self._append_rows(rows)

            # Trier par ml_score (colonne I)
            self._sort_by_ml_score()

            # Archiver les vieilles offres si nécessaire
            self._archive_old_offers()

            logger.info(f"✅ {len(new_jobs)} offres ajoutées avec succès")
            return len(new_jobs)

        except HttpError as e:
            logger.error(f"Erreur HTTP Google Sheets: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des offres: {str(e)}")
            raise

    def _ensure_header_exists(self):
        """Vérifie que le header existe, sinon le crée"""
        try:
            # Lire la première ligne
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range='A1:L1'
            ).execute()

            values = result.get('values', [])

            if not values or values[0] != get_header_row():
                logger.info("Création du header...")
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.sheet_id,
                    range='A1:L1',
                    valueInputOption='RAW',
                    body={'values': [get_header_row()]}
                ).execute()

        except HttpError as e:
            logger.error(f"Erreur lors de la vérification du header: {str(e)}")
            raise

    def _get_existing_urls(self) -> set:
        """Récupère les URLs déjà présentes dans le Sheet (colonne H)"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range='H:H'  # Colonne job_url
            ).execute()

            values = result.get('values', [])
            # Exclure le header (première ligne)
            urls = {row[0] for row in values[1:] if row and row[0]}
            return urls

        except HttpError:
            # Si la colonne est vide, retourner un set vide
            return set()

    def _append_rows(self, rows: List[List]):
        """Ajoute des lignes au Sheet"""
        try:
            self.service.spreadsheets().values().append(
                spreadsheetId=self.sheet_id,
                range='A:L',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()

        except HttpError as e:
            logger.error(f"Erreur lors de l'ajout des lignes: {str(e)}")
            raise

    def _sort_by_ml_score(self):
        """Trie le Sheet par ml_score (colonne I) en ordre décroissant"""
        try:
            # Récupérer le nombre de lignes
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range='A:A'
            ).execute()

            num_rows = len(result.get('values', []))

            if num_rows <= 1:
                return

            # Requête de tri
            requests = [{
                'sortRange': {
                    'range': {
                        'sheetId': 0,  # Première feuille
                        'startRowIndex': 1,  # Exclure le header
                        'endRowIndex': num_rows,
                        'startColumnIndex': 0,
                        'endColumnIndex': 12
                    },
                    'sortSpecs': [{
                        'dimensionIndex': 8,  # Colonne I (ml_score)
                        'sortOrder': 'DESCENDING'
                    }]
                }
            }]

            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id,
                body={'requests': requests}
            ).execute()

            logger.info("✅ Sheet trié par ml_score")

        except HttpError as e:
            logger.warning(f"Impossible de trier le Sheet: {str(e)}")

    def _archive_old_offers(self):
        """
        Archive les offres > 14 jours (optionnel)
        Pour l'instant, on limite juste à 50 offres
        """
        try:
            # Récupérer toutes les lignes
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range='A:L'
            ).execute()

            values = result.get('values', [])

            if len(values) > 51:  # Header + 50 offres
                logger.info(f"Limitation à 50 offres (actuellement {len(values) - 1})")
                # Supprimer les lignes au-delà de 51
                requests = [{
                    'deleteDimension': {
                        'range': {
                            'sheetId': 0,
                            'dimension': 'ROWS',
                            'startIndex': 51,
                            'endIndex': len(values)
                        }
                    }
                }]

                self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.sheet_id,
                    body={'requests': requests}
                ).execute()

                logger.info("✅ Offres anciennes archivées")

        except HttpError as e:
            logger.warning(f"Impossible d'archiver les vieilles offres: {str(e)}")
