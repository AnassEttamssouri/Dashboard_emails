"""Génère data/emails.csv (7 jours d'emails fictifs). Relancer pour rafraîchir les dates."""
import os
import random
from datetime import datetime, timedelta

import pandas as pd

from email_utils import creer_email_fictif

CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'emails.csv')


def generate(days=7):
    random.seed(42)
    fin = datetime.now().replace(minute=0, second=0, microsecond=0)
    rows = []
    for h in range(days * 24, 0, -1):
        base = fin - timedelta(hours=h)
        for _ in range(random.randint(0, 3)):
            rows.append(creer_email_fictif('reçu', random.choice(['réclamation', 'commande', 'support']),
                                           base + timedelta(minutes=random.randint(0, 59))))
        for _ in range(random.randint(0, 2)):
            rows.append(creer_email_fictif('envoyé', random.choice(['vente', 'support']),
                                           base + timedelta(minutes=random.randint(0, 59))))
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    pd.DataFrame(rows).to_csv(CSV_PATH, index=False)
    return CSV_PATH


if __name__ == '__main__':
    print('Fichier créé :', generate())
