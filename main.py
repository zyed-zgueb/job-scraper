"""
Job Scraper - Point d'entrée principal
Scrape Indeed + HelloWork, classifie avec ML, et popule Google Sheets
"""

import sys
from datetime import datetime
from utils.config import Config
from utils.logger import setup_logger
from scraper.indeed_scraper import IndeedScraper
from scraper.hellowork_scraper import HelloWorkScraper
from classifier.ml_classifier import MLClassifier
from sheets.google_sheets_api import GoogleSheetsAPI
from notifier.email_sender import EmailSender

logger = setup_logger(__name__)


def main():
    """Fonction principale d'exécution"""
    try:
        logger.info("=" * 80)
        logger.info(f"🚀 Démarrage du Job Scraper - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

        # Chargement de la configuration
        config = Config()
        logger.info("✅ Configuration chargée")

        # Initialisation des scrapers
        indeed_scraper = IndeedScraper(config)
        hellowork_scraper = HelloWorkScraper(config)

        # Scraping des offres
        logger.info("\n📊 Phase 1: Scraping des offres...")
        indeed_jobs = indeed_scraper.scrape()
        logger.info(f"  Indeed: {len(indeed_jobs)} offres trouvées")

        hellowork_jobs = hellowork_scraper.scrape()
        logger.info(f"  HelloWork: {len(hellowork_jobs)} offres trouvées")

        all_jobs = indeed_jobs + hellowork_jobs
        logger.info(f"  Total: {len(all_jobs)} offres")

        if not all_jobs:
            logger.warning("⚠️ Aucune offre trouvée. Arrêt du programme.")
            return

        # Classification ML
        logger.info("\n🤖 Phase 2: Classification ML...")
        classifier = MLClassifier(config)
        classified_jobs = classifier.classify_jobs(all_jobs)
        logger.info(f"  {len(classified_jobs)} offres passent le seuil ML ({config.ml_score_threshold})")

        if not classified_jobs:
            logger.warning("⚠️ Aucune offre n'a passé le seuil ML. Arrêt du programme.")
            return

        # Google Sheets
        logger.info("\n📝 Phase 3: Mise à jour Google Sheets...")
        if not config.dry_run:
            sheets_api = GoogleSheetsAPI(config)
            new_jobs_count = sheets_api.append_jobs(classified_jobs)
            logger.info(f"  {new_jobs_count} nouvelles offres ajoutées au Sheet")
        else:
            logger.info("  DRY RUN activé - pas d'écriture au Sheet")
            new_jobs_count = len(classified_jobs)

        # Envoi d'email
        logger.info("\n📧 Phase 4: Envoi de l'email quotidien...")
        if not config.dry_run and new_jobs_count > 0:
            email_sender = EmailSender(config)
            top_jobs = sorted(classified_jobs, key=lambda x: x['ml_score'], reverse=True)[:5]
            email_sender.send_daily_digest(top_jobs, len(all_jobs), new_jobs_count)
            logger.info("  Email envoyé avec succès")
        else:
            if config.dry_run:
                logger.info("  DRY RUN activé - pas d'envoi d'email")
            else:
                logger.info("  Pas de nouvelles offres - pas d'email envoyé")

        # Résumé final
        logger.info("\n" + "=" * 80)
        logger.info("✅ Exécution terminée avec succès!")
        logger.info(f"   📊 Offres scrapées: {len(all_jobs)}")
        logger.info(f"   🎯 Offres qualifiées ML: {len(classified_jobs)}")
        logger.info(f"   ➕ Nouvelles offres ajoutées: {new_jobs_count}")
        logger.info("=" * 80)

    except KeyboardInterrupt:
        logger.info("\n⚠️ Interruption manuelle - Arrêt du programme")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Erreur fatale: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
