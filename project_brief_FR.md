# 📋 BRIEF - JOB SCRAPER ML + GOOGLE SHEETS AUTOMATION

## 1. OBJECTIF GLOBAL

Créer un **scraper de job boards automatisé** qui :
- Scrape **Indeed** + **HelloWork** quotidiennement
- Filtre les offres basées sur des critères précis (salaire, localisation, seniority)
- **Classifie automatiquement** chaque offre via ML (sentence-transformers) pour évaluer le match avec le profil utilisateur
- Peuple un **Google Sheet** avec les offres triées et scorées
- Envoie un **email quotidien** synthétique (top 5 offres)
- Déployé sur **GitHub Actions** (exécution automatique 1x/jour)

---

## 2. ARCHITECTURE GÉNÉRALE

```
Indeed API + HelloWork Scraping
            ↓
    [Cleaning + Parsing]
            ↓
    [Classification ML: sentence-transformers]
    (embedding offre vs profil utilisateur)
            ↓
    [Filtering: salaire > 50k, localisation OK, score ML > seuil]
            ↓
    [Google Sheets API: append rows]
    [Email SMTP: send daily digest]
            ↓
GitHub Actions: cron job 1x/day (ex: 9h du matin)
```

---

## 3. SPÉCIFICATIONS DÉTAILLÉES

### 3.1 SCRAPING

**Indeed** :
- Utiliser la **RapidAPI Indeed API** (gratuit, 100 requêtes/mois)
  - Ou web scraping avec `requests` + `BeautifulSoup` si API trop limité
- Query : `"Engineering Manager" OR "Tech Lead" OR "Product Manager" OR "Senior Developer" location:France`
- Extraire : title, company, location, salary, job_url, description, date_posted

**HelloWork** :
- Web scraping avec `BeautifulSoup` + optionnellement `Selenium`
- URL base : `https://www.hellowork.com/fr-fr/emploi/recherche.html`
- Query params : keywords + location (Nancy, Metz, Épinal)
- Extraire : title, company, location, salary, job_url, description, date_posted

**Robustesse** :
- Retry logic (3 tentatives avec backoff exponentiel)
- User-Agent rotation (HelloWork bloque les scrapers)
- Caching : ne pas rescraper la même offre 2x (vérifier job_url en BD)

### 3.2 CLASSIFICATION ML

**Modèle** : `sentence-transformers` (modèle pré-entraîné `multilingual-MiniLM-L12-v2` ou équivalent)

**Profil utilisateur** : Créer un "profil embedding" basé sur :
```
Engineering Manager | Product Manager | Tech Lead | Senior Developer
20+ years experience
Full stack + AI/LLM
Python, Swift, Java, C#, PHP, Vue.js, Laravel
Product strategy, team leadership, technical architecture
AI integration, LLM APIs, conversational agents
```

**Classification** :
- Pour chaque offre : créer embedding (titre + description)
- Calculer **cosine similarity** entre offre et profil
- Attribuer un **score de match (0-100)** : `similarity * 100`
- Garder offres avec score > **65** (configurable)

**Entraînement** :
- **Optionnel** : si l'utilisateur fournit 5-10 exemples d'offres "bonnes" (liens), affiner avec une petite fine-tune
- **Sans entraînement** : démarrer avec le profil texte brut (fonctionne déjà bien)

### 3.3 FILTRES STRICTS (avant ML)

Appliquer **avant** la classification ML :

| Critère | Règle |
|---------|-------|
| **Salaire** | `salary_min >= 50000 EUR` (si absent, inclure mais marquer "TBD") |
| **Localisation** | Contient : Nancy, Metz, Épinal, Lorraine OR "remote" (mais déprioritiser remote) |
| **Type emploi** | CDI prioritaire (exclure stage/freelance sauf mention "freelance OK") |
| **Entreprise** | Scale-up (10-500p) ou Grosse boîte (>500p) — exclure micro-startups |
| **Doublons** | Ne pas ajouter si job_url déjà présent en Sheet |

### 3.4 GOOGLE SHEETS API

**Sheet ID** : `1GGSmY3x2a-Y1UekDGTx--04Uib8hhuzf5fT7zu3bYBc`

**Structure colonnes** (créer header si absent) :
| Col | Nom | Type | Notes |
|-----|-----|------|-------|
| A | date_added | DATE | AUJOURD'HUI() |
| B | source | TEXT | "Indeed" ou "HelloWork" |
| C | title | TEXT | Titre de l'offre |
| D | company | TEXT | Nom entreprise |
| E | location | TEXT | Ville/région |
| F | salary_min | NUMBER | En EUR, ou "TBD" |
| G | salary_max | NUMBER | En EUR, ou vide |
| H | job_url | HYPERLINK | Lien cliquable |
| I | ml_score | NUMBER | 0-100 (cosine similarity) |
| J | status | TEXT | Dropdown: ["À appliquer", "Skip", "En cours", "Rejeté", ""] |
| K | notes | TEXT | Notes personnelles (auto-rempli vide) |
| L | description_short | TEXT | Premiers 200 caractères de la description |

**Logique d'ajout** :
- Vérifier que job_url n'existe pas déjà (colonne H)
- Ajouter nouvelles offres au **bas du Sheet** (append mode)
- Trier automatiquement par `ml_score` DESC (meilleures offres en haut)
- Limiter à **50 dernières offres** pour garder le Sheet lisible (archiver les plus vieilles)

### 3.5 EMAIL QUOTIDIEN

**Service** : SMTP Gmail (tu auras besoin d'une app password)

**Contenu** :
```
Subject: 📊 Job Scraper - Top offres du jour

Bonjour Vincent,

Voici les 5 meilleures offres du jour (score ML > 75):

1. [Title] @ [Company]
   📍 [Location] | 💰 [Salary] | Score: [ML_SCORE]%
   → [Lien clickable]

2. ...

---
📈 Stats du jour: 12 offres trouvées, 5 ont passé les filtres
🔗 Voir toutes les offres: [Lien Google Sheet]

(Email auto-généré par Job Scraper)
```

---

## 4. DONNÉES D'ENTRÉE / CONFIGURATION

**Fichier `.env`** (à créer) :
```
# Google Sheets
GOOGLE_SHEET_ID=1GGSmY3x2a-Y1UekDGTx--04Uib8hhuzf5fT7zu3bYBc
GOOGLE_CREDS_JSON=./creds.json  # fichier à créer via Google Cloud Console

# Email SMTP
SMTP_EMAIL=zyed.zgueb@gmail.com
SMTP_PASSWORD=xxxxx  # Google App Password
SMTP_RECIPIENT=zyed.zgueb@gmail.com

# Filtres
MIN_SALARY=50000
LOCATIONS=Nancy,Metz,Épinal,remote
ML_SCORE_THRESHOLD=65
MAX_REMOTE_DISTANCE_KM=100

# Indeed API
INDEED_API_KEY=xxxxx  # Si utilisé (optionnel)

# Comportement
DRY_RUN=false  # true = test sans écrire en Sheet
DEBUG=false
```

**Profil utilisateur** (à intégrer en dur dans le code ou config) :
```
PROFILE_TEXT = """
Engineering Manager, Tech Lead, Product Manager, Senior Developer
20+ years experience in full stack development
Expertise: Python, Swift, iOS, Android, Java, C#, PHP, Laravel, Vue.js
Product strategy, team management, technical leadership
AI/LLM integration, conversational agents, computer vision
Scale-up ou grosse boîte (éviter micro-startups)
"""
```

---

## 5. STRUCTURE TECHNIQUE

**Stack** :
- **Python 3.10+**
- **Dependencies** :
  - `requests` : HTTP calls (Indeed, HelloWork)
  - `beautifulsoup4` : web scraping
  - `selenium` : optionnel (si scraping complexe)
  - `google-api-python-client` : Google Sheets API
  - `google-auth-oauthlib` : Google auth
  - `sentence-transformers` : ML classification
  - `python-dotenv` : config .env
  - `smtplib` + `email` : sending emails

**Structure fichiers** :
```
job-scraper/
├── main.py                    # Point d'entrée
├── scraper/
│   ├── indeed_scraper.py      # Indeed API/scraping
│   ├── hellowork_scraper.py   # HelloWork scraping
│   └── base_scraper.py        # Classes commune
├── classifier/
│   ├── ml_classifier.py       # sentence-transformers logic
│   └── profile.py             # Profil utilisateur
├── sheets/
│   ├── google_sheets_api.py   # Google Sheets operations
│   └── formatter.py           # Data formatting
├── notifier/
│   ├── email_sender.py        # SMTP email
│   └── templates.py           # Email templates
├── utils/
│   ├── config.py              # Configuration loading
│   ├── logger.py              # Logging
│   └── helpers.py             # Utility functions
├── .github/workflows/
│   └── daily_scrape.yml       # GitHub Actions cron
├── requirements.txt
├── .env.example
├── README.md
└── creds.json                 # Google auth (à créer)
```

---

## 6. WORKFLOW DÉTAILLÉ

**Exécution quotidienne (GitHub Actions à 9h)** :

1. **Scraping parallèle** (async) :
   - Indeed API : fetch offres
   - HelloWork scraping : fetch offres
   - Cache : vérifier qu'on n'a pas la même offre

2. **Nettoyage / Parsing** :
   - Normaliser les salaires (min/max en EUR)
   - Normaliser les localisations
   - Extraire le type d'emploi (CDI/stage/etc)
   - Nettoyer HTML/accents/doublons

3. **Filtrage stricts** :
   - `salary >= 50k` ?
   - `location in [Nancy, Metz, Épinal, remote]` ?
   - `company_size in [scale-up, big]` ?
   - `job_url not in Sheet` ?
   - Garder ~100-200 offres après ce filtre

4. **Classification ML** :
   - Pour chaque offre restante :
     - Créer embedding (titre + description)
     - Calculer similarity vs profil
     - Assigner score (0-100)
   - Garder offres avec score > 65

5. **Google Sheets** :
   - Append rows pour offres qualifiées
   - Trier par ml_score DESC
   - Archiver offres > 7 jours (ou move to archive sheet)
   - Update formules (si besoin)

6. **Email** :
   - Créer liste top 5
   - Formatter email HTML
   - Envoyer via SMTP

7. **Logging** :
   - Enregistrer : "X offres scrapées, Y filtrées, Z ajoutées au Sheet"
   - Stocker logs pour debugging

---

## 7. DÉPLOIEMENT GITHUB ACTIONS

**Fichier `.github/workflows/daily_scrape.yml`** :

```yaml
name: Daily Job Scraper

on:
  schedule:
    - cron: '0 9 * * *'  # 9h du matin, tous les jours (UTC+1 = 8h UTC)
  workflow_dispatch:  # Permet de trigger manuellement

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Create .env
        env:
          GOOGLE_CREDS: ${{ secrets.GOOGLE_CREDS }}
          SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}
        run: |
          echo "$GOOGLE_CREDS" > creds.json
          cat > .env << EOF
          GOOGLE_SHEET_ID=${{ secrets.GOOGLE_SHEET_ID }}
          SMTP_EMAIL=${{ secrets.SMTP_EMAIL }}
          SMTP_PASSWORD=$SMTP_PASSWORD
          SMTP_RECIPIENT=${{ secrets.SMTP_RECIPIENT }}
          MIN_SALARY=50000
          EOF
      
      - name: Run scraper
        run: python main.py
```

**GitHub Secrets à configurer** :
- `GOOGLE_CREDS` : contenu du fichier `creds.json`
- `GOOGLE_SHEET_ID` : ton sheet ID
- `SMTP_EMAIL`, `SMTP_PASSWORD`, `SMTP_RECIPIENT`

---

## 8. EDGE CASES & ROBUSTESSE

**Gestion d'erreurs** :
- API Indeed indisponible → continuer avec HelloWork
- Scraping HelloWork bloqué → retry avec backoff + user-agent rotation
- Google Sheets API rate limit → queue + retry
- Email SMTP échoue → log error mais ne crash pas le scraper

**Validation données** :
- Salaire manquant → inclure mais marquer "TBD"
- Localisation vague ("France") → exclure (trop imprécis)
- Offre très courte (< 50 caractères) → suspect, vérifier manuellement
- Score ML très bas (< 30) → exclure automatiquement

**Duplicates** :
- Vérifier job_url (colonne H) avant d'ajouter
- Vérifier aussi `[company, title, location]` en cas d'URL légèrement différente

**Nettoyage periodique** :
- Archiver offres > 14 jours (move to "archive" sheet)
- Supprimer offres rejetées > 30 jours

---

## 9. LIVRABLES ATTENDUS

1. **Code Python** : structure complète + fonctionnel
2. **`.env.example`** : template de configuration
3. **`requirements.txt`** : dépendances
4. **`.github/workflows/daily_scrape.yml`** : GitHub Actions workflow
5. **`README.md`** : 
   - Setup instructions (Google auth, secrets GitHub, etc)
   - Comment tourner localement
   - Comment customiser filtres/profil
6. **`config_example.json`** : exemple de profil utilisateur à customiser

---

## 10. NOTES IMPORTANTES

- **ML sans entraînement** : ça marche déjà correctement avec le profil texte brut. Si besoin de mieux, tu peux ajouter examples plus tard.
- **Performance** : scraping + ML classifie ~100 offres en 2-3 min
- **Coûts** : gratuit (Indeed API free tier + GitHub Actions free)
- **Maintenance** : zéro après setup (GitHub Actions handle le reste)

---

## 11. QUESTIONS POUR L'IMPLÉMENTATION

**Avant de coder, clarifier** :
- Indeed API vs web scraping ? (recommande : web scraping, c'est plus flexible)
- Faut-il un "training set" pour la classification ML ou on démarre avec le profil texte brut ? (recommande : profil texte brut, on affine plus tard si besoin)
- Veux-tu une archive sheet ou juste supprimer les vieilles offres ? (recommande : archive sheet)

---

Voilà ! **C'est un brief très complet et précis**. Copie-colle ça dans Claude Code et il devrait pouvoir l'implémenter sans ambiguïté. 

**Avant de lui donner**, tu dois préparer :

1. **Google Service Account** (pour l'authentification Sheet) :
   - Va sur https://console.cloud.google.com
   - Crée un nouveau projet
   - Enable "Google Sheets API"
   - Crée une "Service Account" + download le JSON
   - Partage ton Sheet avec l'email du service account

2. **Gmail App Password** (pour SMTP) :
   - Va sur https://myaccount.google.com/apppasswords
   - Crée une app password pour "Mail"
   - Note-le (tu le mettras en secret GitHub)