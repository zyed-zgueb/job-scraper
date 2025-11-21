"""
Scraper pour HelloWork
Web scraping avec BeautifulSoup (+ optionnellement Selenium si besoin)
"""

from typing import List, Dict
from datetime import datetime
from .base_scraper import BaseScraper
from utils.logger import setup_logger

logger = setup_logger(__name__)


class HelloWorkScraper(BaseScraper):
    """Scraper pour le site HelloWork"""

    BASE_URL = "https://www.hellowork.com"
    SEARCH_URL = f"{BASE_URL}/fr-fr/emplois/recherche.html"

    def scrape(self) -> List[Dict]:
        """
        Scrape les offres d'emploi depuis HelloWork

        Returns:
            Liste des offres formatées
        """
        logger.info("Scraping HelloWork...")

        jobs = []
        keywords = [
            "Engineering Manager",
            "Tech Lead",
            "Product Manager",
            "Senior Developer"
        ]

        # Locations spécifiques du brief
        locations = ["Nancy", "Metz", "Épinal"]

        for keyword in keywords:
            for location in locations:
                logger.info(f"  Recherche: {keyword} @ {location}")
                jobs_for_query = self._search_jobs(keyword, location)
                jobs.extend(jobs_for_query)
                logger.info(f"  Trouvé: {len(jobs_for_query)} offres")

        # Dédupliquer
        unique_jobs = self._deduplicate_jobs(jobs)
        logger.info(f"Total après déduplication: {len(unique_jobs)} offres")

        # Filtrer selon critères
        filtered_jobs = self.filter_by_criteria(unique_jobs)
        logger.info(f"Après filtrage: {len(filtered_jobs)} offres")

        return filtered_jobs

    def _search_jobs(self, keyword: str, location: str) -> List[Dict]:
        """
        Recherche des offres pour un mot-clé et une localisation

        Args:
            keyword: Mot-clé de recherche
            location: Localisation

        Returns:
            Liste des offres trouvées
        """
        jobs = []

        params = {
            'k': keyword,
            'l': location,
            'd': '7',  # Derniers 7 jours
        }

        try:
            response = self.make_request(self.SEARCH_URL, params=params, timeout=10)
            if not response:
                logger.error(f"Échec de la requête pour {keyword} @ {location}")
                return jobs

            soup = self.parse_html(response.text)

            # HelloWork utilise des cards pour chaque offre
            # La structure HTML peut varier, ceci est une approximation
            job_cards = soup.find_all('article', class_='job-card') or \
                        soup.find_all('div', class_='offer-card') or \
                        soup.find_all('li', class_='offer-item')

            if not job_cards:
                logger.debug(f"Aucune carte d'offre trouvée pour {keyword} @ {location}")
                return jobs

            for card in job_cards:
                try:
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"Erreur lors du parsing d'une carte: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Erreur lors du scraping HelloWork pour '{keyword}' @ '{location}': {str(e)}")

        return jobs

    def _parse_job_card(self, card) -> Dict:
        """
        Parse une carte d'offre HelloWork

        Args:
            card: Element BeautifulSoup de la carte

        Returns:
            Dictionnaire avec les données de l'offre
        """
        try:
            # Titre - adapter selon la structure HTML réelle
            title_elem = card.find('h2') or card.find('h3') or card.find('a', class_='job-title')
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # Entreprise
            company_elem = card.find('div', class_='company') or \
                          card.find('span', class_='company-name') or \
                          card.find('p', class_='company')
            company = company_elem.get_text(strip=True) if company_elem else "N/A"

            # Localisation
            location_elem = card.find('div', class_='location') or \
                           card.find('span', class_='location')
            location = location_elem.get_text(strip=True) if location_elem else "N/A"

            # URL
            link_elem = card.find('a', href=True)
            job_url = ""
            if link_elem and 'href' in link_elem.attrs:
                href = link_elem['href']
                job_url = href if href.startswith('http') else f"{self.BASE_URL}{href}"

            # Salaire (optionnel)
            salary_elem = card.find('div', class_='salary') or \
                         card.find('span', class_='salary')
            salary_text = salary_elem.get_text(strip=True) if salary_elem else ""
            salary_data = self.normalize_salary(salary_text)

            # Description courte
            description_elem = card.find('div', class_='description') or \
                              card.find('p', class_='description')
            description = description_elem.get_text(strip=True) if description_elem else ""

            return {
                'source': 'HelloWork',
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
            logger.debug(f"Erreur parsing carte HelloWork: {str(e)}")
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
