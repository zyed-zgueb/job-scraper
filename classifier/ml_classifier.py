"""
Classification ML des offres d'emploi
Utilise sentence-transformers pour calculer la similarité avec le profil utilisateur
"""

from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer, util
from .profile import PROFILE_TEXT
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MLClassifier:
    """Classifieur ML pour évaluer le match offre/profil"""

    def __init__(self, config):
        self.config = config
        self.model_name = 'paraphrase-multilingual-MiniLM-L12-v2'
        logger.info(f"Chargement du modèle ML: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)

        # Créer l'embedding du profil utilisateur
        logger.info("Création de l'embedding du profil utilisateur...")
        self.profile_embedding = self.model.encode(PROFILE_TEXT, convert_to_tensor=True)
        logger.info("✅ Modèle ML prêt")

    def classify_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Classifie les offres et calcule un score de match

        Args:
            jobs: Liste des offres à classifier

        Returns:
            Liste des offres avec score ML > threshold
        """
        if not jobs:
            return []

        logger.info(f"Classification de {len(jobs)} offres...")

        scored_jobs = []
        for job in jobs:
            try:
                score = self._calculate_match_score(job)
                job['ml_score'] = score

                if score >= self.config.ml_score_threshold:
                    scored_jobs.append(job)
                    logger.debug(f"✓ Score {score:.1f}: {job['title']} @ {job['company']}")
                else:
                    logger.debug(f"✗ Score {score:.1f}: {job['title']} @ {job['company']}")

            except Exception as e:
                logger.error(f"Erreur lors de la classification de {job.get('title', 'N/A')}: {str(e)}")
                continue

        # Trier par score décroissant
        scored_jobs.sort(key=lambda x: x['ml_score'], reverse=True)

        logger.info(f"✅ {len(scored_jobs)} offres passent le seuil ({self.config.ml_score_threshold})")
        return scored_jobs

    def _calculate_match_score(self, job: Dict) -> float:
        """
        Calcule le score de match pour une offre

        Args:
            job: Dictionnaire de l'offre

        Returns:
            Score de 0 à 100
        """
        # Combiner titre + description pour l'analyse
        job_text = f"{job['title']} {job.get('description', '')}"

        # Créer l'embedding de l'offre
        job_embedding = self.model.encode(job_text, convert_to_tensor=True)

        # Calculer la similarité cosine
        cosine_score = util.cos_sim(self.profile_embedding, job_embedding)

        # Convertir en score 0-100
        score = float(cosine_score.cpu().numpy()[0][0]) * 100

        return round(score, 2)

    def fine_tune(self, positive_examples: List[str], negative_examples: List[str] = None):
        """
        Fine-tune le modèle avec des exemples (optionnel)

        Args:
            positive_examples: Liste d'URLs ou textes d'offres "bonnes"
            negative_examples: Liste d'URLs ou textes d'offres "mauvaises"

        Note:
            Cette fonctionnalité est optionnelle et peut être implémentée plus tard
        """
        # TODO: Implémenter le fine-tuning si nécessaire
        logger.warning("Fine-tuning non encore implémenté - utilisation du modèle pré-entraîné")
        pass
