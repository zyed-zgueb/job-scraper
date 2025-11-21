"""
Templates d'emails
"""

from typing import List, Dict


def format_daily_digest(top_jobs: List[Dict], total_scraped: int, total_added: int, sheet_url: str) -> str:
    """
    Génère le contenu HTML de l'email quotidien

    Args:
        top_jobs: Top 5 des meilleures offres
        total_scraped: Nombre total d'offres scrapées
        total_added: Nombre d'offres ajoutées au Sheet
        sheet_url: URL du Google Sheet

    Returns:
        Contenu HTML de l'email
    """
    jobs_html = ""

    for i, job in enumerate(top_jobs, 1):
        salary_min = job.get('salary_min')
        salary_max = job.get('salary_max')

        if salary_min and salary_max and salary_min != salary_max:
            salary_str = f"{int(salary_min):,}€ - {int(salary_max):,}€"
        elif salary_min:
            salary_str = f"{int(salary_min):,}€"
        else:
            salary_str = "TBD"

        jobs_html += f"""
        <div style="margin: 20px 0; padding: 15px; background-color: #f5f5f5; border-radius: 8px;">
            <h3 style="margin: 0 0 10px 0; color: #2c3e50;">
                {i}. {job.get('title', 'N/A')} @ {job.get('company', 'N/A')}
            </h3>
            <p style="margin: 5px 0; color: #555;">
                📍 <strong>{job.get('location', 'N/A')}</strong> |
                💰 <strong>{salary_str}</strong> |
                🎯 Score: <strong style="color: #27ae60;">{job.get('ml_score', 0):.1f}%</strong>
            </p>
            <p style="margin: 10px 0 0 0;">
                <a href="{job.get('job_url', '#')}"
                   style="color: #3498db; text-decoration: none; font-weight: bold;">
                    → Voir l'offre
                </a>
            </p>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #3498db; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h1 style="margin: 0;">📊 Job Scraper - Top offres du jour</h1>
        </div>

        <p>Bonjour,</p>
        <p>Voici les <strong>{len(top_jobs)} meilleures offres</strong> du jour (score ML > 75):</p>

        {jobs_html}

        <div style="margin: 30px 0; padding: 20px; background-color: #ecf0f1; border-radius: 8px;">
            <h3 style="margin: 0 0 10px 0;">📈 Statistiques du jour</h3>
            <p style="margin: 5px 0;">
                🔍 <strong>{total_scraped}</strong> offres trouvées<br>
                ✅ <strong>{total_added}</strong> offres ajoutées au Sheet
            </p>
        </div>

        <div style="text-align: center; margin: 20px 0;">
            <a href="{sheet_url}"
               style="display: inline-block; padding: 12px 24px; background-color: #27ae60;
                      color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                🔗 Voir toutes les offres dans Google Sheet
            </a>
        </div>

        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;
                    text-align: center; color: #999; font-size: 12px;">
            <p>Email auto-généré par Job Scraper</p>
        </div>
    </body>
    </html>
    """

    return html


def get_subject_line(num_jobs: int) -> str:
    """
    Génère la ligne de sujet de l'email

    Args:
        num_jobs: Nombre d'offres dans l'email

    Returns:
        Ligne de sujet
    """
    if num_jobs == 0:
        return "📊 Job Scraper - Aucune nouvelle offre aujourd'hui"
    elif num_jobs == 1:
        return "📊 Job Scraper - 1 nouvelle offre"
    else:
        return f"📊 Job Scraper - {num_jobs} nouvelles offres"
