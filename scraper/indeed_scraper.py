"""
Scraper pour Indeed
Peut utiliser l'API RapidAPI ou du web scraping direct
"""

from typing import List, Dict
from datetime import datetime
import time
import random
from .base_scraper import BaseScraper
from utils.logger import setup_logger

logger = setup_logger(__name__)


class IndeedScraper(BaseScraper):
    """Scraper pour le site Indeed"""

    BASE_URL = "https://fr.indeed.com"

    def __init__(self, config):
        super().__init__(config)
        self.use_api = hasattr(config, 'indeed_api_key') and config.indeed_api_key

    def scrape(self) -> List[Dict]:
        """
        Scrape les offres d'emploi depuis Indeed

        Returns:
            Liste des offres formatées
        """
        logger.info("Scraping Indeed...")

        if self.use_api:
            return self._scrape_with_api()
        else:
            return self._scrape_with_web()

    def _scrape_with_api(self) -> List[Dict]:
        """Scraping via RapidAPI Indeed API"""
        logger.info("Utilisation de l'API Indeed (RapidAPI)")

        # TODO: Implémenter l'API RapidAPI si configurée
        # Pour l'instant, on utilise le web scraping
        logger.warning("API Indeed non encore implémentée, basculement sur web scraping")
        return self._scrape_with_web()

    def _scrape_with_web(self) -> List[Dict]:
        """Scraping direct du site web Indeed"""
        logger.info("Web scraping Indeed...")

        jobs = []
        keywords = [
            "Engineering Manager",
            "Tech Lead",
            "Product Manager",
            "Senior Developer",
            "Chef de projet"
        ]

        for i, keyword in enumerate(keywords):
            logger.info(f"  Recherche: {keyword}")
            jobs_for_keyword = self._search_jobs(keyword)
            jobs.extend(jobs_for_keyword)
            logger.info(f"  Trouvé: {len(jobs_for_keyword)} offres")

            # Délai entre les requêtes pour éviter d'être bloqué (sauf pour la dernière)
            if i < len(keywords) - 1:
                delay = random.uniform(2, 5)
                logger.debug(f"  Attente de {delay:.1f}s avant la prochaine recherche...")
                time.sleep(delay)

        # Dédupliquer par URL
        unique_jobs = self._deduplicate_jobs(jobs)
        logger.info(f"Total après déduplication: {len(unique_jobs)} offres")

        # Filtrer selon critères
        filtered_jobs = self.filter_by_criteria(unique_jobs)
        logger.info(f"Après filtrage: {len(filtered_jobs)} offres")

        return filtered_jobs

    def _search_jobs(self, keyword: str) -> List[Dict]:
        """
        Recherche des offres pour un mot-clé donné

        Args:
            keyword: Mot-clé de recherche

        Returns:
            Liste des offres trouvées
        """
        jobs = []
        base_search_url = f"{self.BASE_URL}/jobs"

        params = {
            'q': keyword,
            'l': 'France',
            'sort': 'date',
            'fromage': '7',  # Derniers 7 jours
        }

        try:
            response = self.make_request(base_search_url, params=params, timeout=10)
            if not response:
                logger.error(f"Échec de la requête pour {keyword}")
                return jobs

            soup = self.parse_html(response.text)

            # Indeed utilise des cards pour chaque offre
            # Structure HTML peut varier, adapter selon la version du site
            job_cards = soup.find_all('div', class_='job_seen_beacon')

            for card in job_cards:
                try:
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"Erreur lors du parsing d'une carte: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Erreur lors du scraping Indeed pour '{keyword}': {str(e)}")

        return jobs

    def _parse_job_card(self, card) -> Dict:
        """
        Parse une carte d'offre Indeed

        Args:
            card: Element BeautifulSoup de la carte

        Returns:
            Dictionnaire avec les données de l'offre
        """
        try:
            # Titre
            title_elem = card.find('h2', class_='jobTitle')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # Entreprise
            company_elem = card.find('span', {'data-testid': 'company-name'})
            company = company_elem.get_text(strip=True) if company_elem else "N/A"

            # Localisation
            location_elem = card.find('div', {'data-testid': 'text-location'})
            location = location_elem.get_text(strip=True) if location_elem else "N/A"

            # URL
            link_elem = title_elem.find('a')
            job_url = f"{self.BASE_URL}{link_elem['href']}" if link_elem and 'href' in link_elem.attrs else ""

            # Salaire (optionnel)
            salary_elem = card.find('div', class_='salary-snippet')
            salary_text = salary_elem.get_text(strip=True) if salary_elem else ""
            salary_data = self.normalize_salary(salary_text)

            # Description courte
            description_elem = card.find('div', class_='job-snippet')
            description = description_elem.get_text(strip=True) if description_elem else ""

            return {
                'source': 'Indeed',
                'title': title,
                'company': company,
                'location': location,
                'salary_min': salary_data['min'],
                'salary_max': salary_data['max'],
                'job_url': job_url,
                'description': description,
                'date_posted': datetime.now().strftime('%Y-%m-%d'),
            }

        except Exception as e:
            logger.debug(f"Erreur parsing carte Indeed: {str(e)}")
            return None

    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Supprime les doublons basés sur job_url"""
        seen_urls = set()
        unique_jobs = []

        for job in jobs:
            url = job.get('job_url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_jobs.append(job)

        return unique_jobs
