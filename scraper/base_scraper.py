"""
Classe de base pour les scrapers
"""

import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseScraper(ABC):
    """Classe abstraite de base pour tous les scrapers"""

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    ]

    def __init__(self, config):
        self.config = config
        self.session = requests.Session()

    def get_random_user_agent(self) -> str:
        """Retourne un User-Agent aléatoire"""
        return random.choice(self.USER_AGENTS)

    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Effectue une requête HTTP avec retry logic et rotation User-Agent

        Args:
            url: URL à requêter
            method: Méthode HTTP (GET, POST, etc.)
            **kwargs: Arguments supplémentaires pour requests

        Returns:
            Response object ou None si échec
        """
        max_retries = 3
        backoff_factor = 2

        headers = kwargs.get('headers', {})
        if 'User-Agent' not in headers:
            headers['User-Agent'] = self.get_random_user_agent()
        kwargs['headers'] = headers

        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, **kwargs)
                else:
                    raise ValueError(f"Méthode HTTP non supportée: {method}")

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                wait_time = backoff_factor ** attempt
                logger.warning(
                    f"Tentative {attempt + 1}/{max_retries} échouée pour {url}: {str(e)}"
                )

                if attempt < max_retries - 1:
                    logger.info(f"Retry dans {wait_time}s...")
                    time.sleep(wait_time)
                    # Rotation du User-Agent pour le retry
                    kwargs['headers']['User-Agent'] = self.get_random_user_agent()
                else:
                    logger.error(f"Échec définitif après {max_retries} tentatives pour {url}")
                    return None

        return None

    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse le contenu HTML avec BeautifulSoup"""
        return BeautifulSoup(html_content, 'html.parser')

    def normalize_salary(self, salary_text: str) -> Dict[str, Optional[int]]:
        """
        Normalise le texte de salaire en min/max EUR

        Args:
            salary_text: Texte brut du salaire

        Returns:
            Dict avec 'min' et 'max' en EUR, ou None si non parsable
        """
        import re

        if not salary_text:
            return {'min': None, 'max': None}

        # Nettoyer le texte
        text = salary_text.lower().replace(' ', '').replace('\xa0', '')

        # Patterns pour EUR
        # Ex: "50000€", "50k€", "50-60k€", "50000-60000€"
        patterns = [
            r'(\d+)k?€?\s*-\s*(\d+)k?€?',  # Range: 50-60k
            r'(\d+)k€?',  # Single: 50k
            r'(\d+)€',  # Single: 50000
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    # Range
                    min_val = int(groups[0])
                    max_val = int(groups[1])
                    # Si en k (< 1000), multiplier par 1000
                    if min_val < 1000:
                        min_val *= 1000
                    if max_val < 1000:
                        max_val *= 1000
                    return {'min': min_val, 'max': max_val}
                else:
                    # Single value
                    val = int(groups[0])
                    if val < 1000:
                        val *= 1000
                    return {'min': val, 'max': val}

        return {'min': None, 'max': None}

    def filter_by_criteria(self, jobs: List[Dict]) -> List[Dict]:
        """
        Filtre les offres selon les critères stricts (salaire, localisation, etc.)

        Args:
            jobs: Liste des offres brutes

        Returns:
            Liste des offres filtrées
        """
        filtered = []
        min_salary = self.config.min_salary
        locations = [loc.lower().strip() for loc in self.config.locations]

        for job in jobs:
            # Filtre salaire
            salary_min = job.get('salary_min')
            if salary_min and salary_min < min_salary:
                logger.debug(f"Rejeté (salaire): {job['title']} @ {job['company']} - {salary_min}€")
                continue

            # Filtre localisation
            job_location = job.get('location', '').lower()
            if not any(loc in job_location for loc in locations):
                logger.debug(f"Rejeté (localisation): {job['title']} - {job_location}")
                continue

            filtered.append(job)

        return filtered

    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Méthode abstraite à implémenter par chaque scraper

        Returns:
            Liste de dictionnaires représentant les offres
        """
        pass
