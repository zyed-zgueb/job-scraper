"""
Envoi d'emails via SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from .templates import format_daily_digest, get_subject_line
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailSender:
    """Gestionnaire d'envoi d'emails"""

    def __init__(self, config):
        self.config = config
        self.smtp_email = config.smtp_email
        self.smtp_password = config.smtp_password
        self.smtp_recipient = config.smtp_recipient
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587

    def send_daily_digest(self, top_jobs: List[Dict], total_scraped: int, total_added: int):
        """
        Envoie l'email quotidien avec le résumé des offres

        Args:
            top_jobs: Top 5 des meilleures offres
            total_scraped: Nombre total d'offres scrapées
            total_added: Nombre d'offres ajoutées
        """
        try:
            logger.info("Préparation de l'email...")

            # URL du Google Sheet
            sheet_url = f"https://docs.google.com/spreadsheets/d/{self.config.google_sheet_id}"

            # Créer le message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = get_subject_line(len(top_jobs))
            msg['From'] = self.smtp_email
            msg['To'] = self.smtp_recipient

            # Corps HTML
            html_body = format_daily_digest(top_jobs, total_scraped, total_added, sheet_url)
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Connexion et envoi
            logger.info("Connexion au serveur SMTP...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)

            logger.info(f"✅ Email envoyé avec succès à {self.smtp_recipient}")

        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Erreur d'authentification SMTP - vérifier email/password")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"❌ Erreur SMTP: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi de l'email: {str(e)}")
            raise
