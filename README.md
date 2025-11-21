# 🔍 Job Smart Scraper

Scraper automatisé de job boards (Indeed + HelloWork) avec classification ML et intégration Google Sheets.

## 📋 Description

Ce projet scrape quotidiennement les offres d'emploi depuis Indeed et HelloWork, les filtre selon des critères précis, utilise du machine learning pour évaluer leur pertinence par rapport à votre profil, et popule automatiquement un Google Sheet avec les meilleures offres. Un email de résumé est envoyé chaque jour.

## ✨ Fonctionnalités

- 🌐 **Scraping multi-sources**: Indeed + HelloWork
- 🤖 **Classification ML**: Utilise sentence-transformers pour scorer chaque offre
- 📊 **Google Sheets**: Popule automatiquement un sheet avec les offres triées
- 📧 **Email quotidien**: Top 5 des meilleures offres du jour
- ⚙️ **GitHub Actions**: Exécution automatique quotidienne
- 🎯 **Filtres personnalisables**: Salaire, localisation, score ML

## 🏗️ Architecture

```
Indeed + HelloWork
        ↓
   [Scraping + Parsing]
        ↓
   [Filtres: salaire, localisation]
        ↓
   [Classification ML: sentence-transformers]
        ↓
   [Google Sheets: append + tri]
   [Email: digest quotidien]
```

## 📁 Structure du projet

```
job-smart-scraper/
├── main.py                    # Point d'entrée
├── scraper/                   # Module de scraping
│   ├── base_scraper.py
│   ├── indeed_scraper.py
│   └── hellowork_scraper.py
├── classifier/                # Classification ML
│   ├── ml_classifier.py
│   └── profile.py
├── sheets/                    # Google Sheets API
│   ├── google_sheets_api.py
│   └── formatter.py
├── notifier/                  # Email notifications
│   ├── email_sender.py
│   └── templates.py
├── utils/                     # Utilitaires
│   ├── config.py
│   ├── logger.py
│   └── helpers.py
├── .github/workflows/         # GitHub Actions
│   └── daily_scrape.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Installation

### Prérequis

- **Python 3.10 ou 3.11** (recommandé)
- Python 3.13 n'est pas encore supporté par toutes les bibliothèques ML

### 1. Cloner le repository

```bash
git clone https://github.com/zyed-zgueb/job-smart-scraper.git
cd job-smart-scraper
```

### 2. Créer un environnement virtuel avec Python 3.11

```bash
# Sur macOS/Linux
python3.11 -m venv venv
source venv/bin/activate

# Sur Windows
python3.11 -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configuration Google Sheets

1. Aller sur [Google Cloud Console](https://console.cloud.google.com)
2. Créer un nouveau projet
3. Activer l'API "Google Sheets API"
4. Créer un "Service Account"
5. Télécharger le fichier JSON des credentials
6. Renommer le fichier en `creds.json` et le placer à la racine du projet
7. Partager votre Google Sheet avec l'email du service account (avec permissions "Éditeur")

### 5. Configuration Email (Gmail)

1. Aller sur [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Créer un mot de passe d'application pour "Mail"
3. Noter le mot de passe généré

### 6. Créer le fichier .env

Copier `.env.example` vers `.env` et remplir les valeurs:

```bash
cp .env.example .env
```

Éditer `.env`:

```env
GOOGLE_SHEET_ID=votre-sheet-id-ici
GOOGLE_CREDS_JSON=./creds.json

SMTP_EMAIL=votre-email@gmail.com
SMTP_PASSWORD=votre-app-password
SMTP_RECIPIENT=votre-email@gmail.com

MIN_SALARY=50000
LOCATIONS=Nancy,Metz,Épinal,remote
ML_SCORE_THRESHOLD=65
```

## Create python virtual environment (optional)
Creating a Virtual Environment in Python
Step 1: Create a Virtual Environment
To create a virtual environment, use the following command in your terminal or command prompt:

```
python -m venv /path/to/new/virtual/environment
```
Replace /path/to/new/virtual/environment with your desired 

directory path. A common practice is to name the directory .venv or venv within your project folder.

Step 2: Activate the Virtual Environment
On Windows:

```
.\path\to\new\virtual\environment\Scripts\activate
```
On macOS/Linux:
```
source /path/to/new/virtual/environment/bin/activate
```
Once activated, your terminal prompt will change to indicate that you are now working within the virtual environment.

Installing Requirements
Step 3: Create a Requirements File (you should already have it)
Create a file named requirements.txt in your project directory. List all the packages you want to install, one per line

Step 4: Install Packages from the Requirements File
With the virtual environment activated, run the following command to install the packages:

```
pip install -r requirements.txt
```
This command will read the requirements.txt file and install all listed packages into your virtual environment.

Conclusion
You now have a virtual environment set up with the necessary packages installed. This setup helps keep your project dependencies organized and isolated from other projects.

## 🔧 Utilisation

### Exécution locale

```bash
python main.py
```

### Mode test (dry run)

Pour tester sans écrire dans le Sheet ni envoyer d'email:

```bash
# Dans .env
DRY_RUN=true
```

## ☁️ Déploiement GitHub Actions

### 1. Configurer les GitHub Secrets

Dans votre repository GitHub: **Settings → Secrets and variables → Actions → New repository secret**

Créer les secrets suivants:

- `GOOGLE_CREDS`: Contenu du fichier `creds.json` (copier-coller tout le JSON)
- `GOOGLE_SHEET_ID`: ID de votre Google Sheet
- `SMTP_EMAIL`: Votre adresse email
- `SMTP_PASSWORD`: Votre app password Gmail
- `SMTP_RECIPIENT`: Email destinataire
- `MIN_SALARY`: (optionnel) Par défaut: 50000
- `ML_SCORE_THRESHOLD`: (optionnel) Par défaut: 65

### 2. Activation

Le workflow s'exécute automatiquement tous les jours à 9h (heure de Paris).

Pour déclencher manuellement: **Actions → Daily Job Scraper → Run workflow**

## 🎯 Personnalisation

### Modifier le profil utilisateur

Éditer `classifier/profile.py` pour adapter le profil ML à vos besoins:

```python
PROFILE_TEXT = """
Votre profil ici...
"""
```

### Modifier les filtres

Dans `.env`:

```env
MIN_SALARY=60000                    # Salaire minimum en EUR
LOCATIONS=Paris,Lyon,remote          # Localisations acceptées
ML_SCORE_THRESHOLD=70                # Score ML minimum (0-100)
```

### Ajouter d'autres sources

Créer un nouveau scraper dans `scraper/` en héritant de `BaseScraper`:

```python
from .base_scraper import BaseScraper

class MonScraper(BaseScraper):
    def scrape(self):
        # Votre logique ici
        pass
```

## 📊 Format Google Sheet

Le script crée automatiquement les colonnes suivantes:

| Colonne | Description |
|---------|-------------|
| date_added | Date d'ajout |
| source | Indeed ou HelloWork |
| title | Titre du poste |
| company | Entreprise |
| location | Localisation |
| salary_min | Salaire min (EUR) |
| salary_max | Salaire max (EUR) |
| job_url | Lien vers l'offre |
| ml_score | Score ML (0-100) |
| status | À remplir manuellement |
| notes | Notes personnelles |
| description_short | Début de la description |

## 🐛 Dépannage

### Erreur de compatibilité des dépendances

Si vous rencontrez des erreurs comme:
- `AttributeError: module 'torch.utils._pytree' has no attribute 'register_pytree_node'`
- `Failed to initialize NumPy: _ARRAY_API not found`
- Conflits de dépendances avec torch/torchvision/numpy

**Solution complète:**

1. Désinstaller toutes les anciennes dépendances ML:
```bash
pip uninstall torch torchvision transformers sentence-transformers numpy -y
```

2. Réinstaller avec les versions compatibles:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Versions fixées pour compatibilité:**
- PyTorch: 2.1.2
- Transformers: 4.37.2 (les versions plus récentes nécessitent PyTorch 2.2+)
- NumPy: ≥1.21.0, <2.0.0 (PyTorch 2.1.2 n'est pas compatible avec NumPy 2.x)

### Erreur d'authentification Google Sheets

- Vérifier que le fichier `creds.json` existe
- Vérifier que le Sheet est partagé avec l'email du service account
- Vérifier que l'API Google Sheets est activée

### Erreur SMTP

- Vérifier que le mot de passe d'application est correct
- Vérifier que l'authentification à 2 facteurs est activée sur Gmail

### Aucune offre trouvée

- Les scrapers peuvent être bloqués par les sites (changer User-Agent)
- La structure HTML des sites peut avoir changé
- Vérifier les logs pour plus de détails

## 📝 TODO / Améliorations futures

- [ ] Support de LinkedIn
- [ ] Fine-tuning du modèle ML avec des exemples
- [ ] Dashboard web pour visualiser les stats
- [ ] Filtres plus avancés (taille entreprise, etc.)
- [ ] Support de Selenium pour scraping plus robuste

## 📄 Licence

MIT

## 👤 Auteur

Projet créé pour automatiser la recherche d'emploi avec ML et automation.
