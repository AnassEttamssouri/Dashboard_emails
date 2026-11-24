"""
Fonctions email - exactement les modules du cours :
smtplib (envoi, diapo 8), email (lecture, diapo 10),
imaplib (filtrage diapo 14, archivage diapo 15), alerte (diapo 16).
"""
import email
import imaplib
import random
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configuration du serveur SMTP (diapo 7)
smtp_server = 'smtp.example.com'
smtp_port = 587
sender_email = 'sender@example.com'
sender_password = 'password'

DESTINATAIRE_ALERTE = 'destinataire@example.com'
MODE_SIMULATION = True   # True : emails fictifs, aucun serveur contacté

SUJETS = {
    'réclamation': ['Colis endommagé', 'Retard de livraison', 'Remboursement demandé'],
    'commande': ['Nouvelle commande #', 'Commande express #', 'Commande en gros #'],
    'support': ['Question sur ma facture', 'Problème de connexion', "Demande d'information"],
    'vente': ['Offre spéciale -20%', 'Devis personnalisé', 'Votre facture de vente'],
    'alerte': ['URGENCE : seuil de commandes dépassé'],
}
CONTACTS = ['amine@mail.com', 'sara@mail.com', 'youssef@mail.com', 'salma@mail.com', 'omar@mail.com']
FORMAT_DATE = '%Y-%m-%d %H:%M:%S'


# ------------------------------------------------------------ Envoi (diapo 8)
def send_email(subject, body, to_email):
    # Création du message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = to_email
    message['Subject'] = subject

    # Corps du message
    message.attach(MIMEText(body, 'plain'))

    if MODE_SIMULATION:
        return 'simulé'

    # Envoi du message
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
        return 'envoyé'
    except Exception as exc:
        return f'échec ({exc})'


# ------------------------------------------------------------ Lecture (diapo 10)
def lire_email(chemin_eml):
    with open(chemin_eml, 'rb') as f:
        msg = email.message_from_bytes(f.read())
    infos = {'Subject': msg['Subject'], 'From': msg.get('From'), 'pieces_jointes': []}
    if msg.is_multipart():
        for part in msg.get_payload():
            if 'attachment' in part.get('Content-Disposition', ''):
                infos['pieces_jointes'].append(part.get_filename())
    return infos


# ------------------------------------------------------------ Filtrage IMAP (diapo 14)
def filter_emails():
    mail = imaplib.IMAP4_SSL('imap.example.com')
    mail.login('votre.email@example.com', 'votre_mot_de_passe')
    mail.select('inbox')
    result, data = mail.search(None, 'UNSEEN')
    email_ids = data[0].split()
    for email_id in email_ids:
        # Traitement des emails non lus ici
        print(email_id)
    return mail, email_ids


# ------------------------------------------------------------ Archivage (diapo 15)
def archive_email(mail, email_id):
    mail.copy(email_id, 'Archive')
    mail.store(email_id, '+FLAGS', '\\Deleted')
    mail.expunge()


# ------------------------------------------------------------ Données fictives
def creer_email_fictif(direction, categorie, quand=None):
    quand = quand or datetime.now()
    sujet = random.choice(SUJETS[categorie])
    if categorie == 'commande':
        sujet += str(random.randint(1000, 9999))
    return {'Date': quand.strftime(FORMAT_DATE), 'direction': direction, 'categorie': categorie,
            'contact': random.choice(CONTACTS), 'sujet': sujet,
            'lu': direction == 'envoyé' or random.random() > 0.4}


# ------------------------------------------------------------ Alerte (diapo 16)
def commandes_heure(records):
    cle = datetime.now().strftime('%Y-%m-%d %H')
    return sum(1 for r in records if r['direction'] == 'reçu'
               and r['categorie'] == 'commande' and r['Date'].startswith(cle))


def condition_met(records, seuil):
    return commandes_heure(records) > seuil


def alert_system(records, seuil, alert_hour):
    """Si condition_met() : envoie l'alerte (une seule fois par heure)."""
    cle = datetime.now().strftime('%Y-%m-%d %H')
    if condition_met(records, seuil) and alert_hour != cle:
        n = commandes_heure(records)
        res = send_email('Alerte', f'Condition remplie! {n} commandes/h (seuil {seuil})', DESTINATAIRE_ALERTE)
        rec = creer_email_fictif('envoyé', 'alerte')
        rec.update(contact=DESTINATAIRE_ALERTE, sujet=f'URGENCE : {n} commandes/h (seuil {seuil})')
        return records + [rec], cle, f"🚨 Alerte d'urgence {res} à {DESTINATAIRE_ALERTE}."
    return records, alert_hour, ''
