"""
Tableau de bord de suivi des emails - Séance N°10
Architecture du cours (diapo 32) : app.py / assets/ / data/ / requirements.txt
Lancer : pip install -r requirements.txt  puis  python app.py  ->  http://127.0.0.1:8050
"""
import os
import re

import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context
import pandas as pd
import plotly.express as px

from email_utils import (alert_system, commandes_heure, creer_email_fictif, send_email)
from generate_data import CSV_PATH, generate

CATEGORIES = ['réclamation', 'commande', 'support', 'vente', 'alerte']


# 1. Chargement et préparation des données avec Pandas (diapo 35)
def prepare_data(records=None):
    if records is None:
        if not os.path.exists(CSV_PATH):
            generate()
        df = pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame(records)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.dropna(subset=['sujet'])
    return df


df_init = prepare_data()
df_init['Date'] = df_init['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

# 2. Initialisation de l'application
app = dash.Dash(__name__)
app.title = 'Dashboard Emails'


def kpi(id_, titre):
    return html.Div([html.Div(titre, className='kpi-title'), html.Div(id=id_, className='kpi-value')],
                    className='kpi')


# 3. Définition du Layout (Interface) - 5 KPI maximum (diapo 40)
app.layout = html.Div(className='container', children=[
    html.H1('📧 Tableau de bord - Suivi des emails'),
    dcc.Store(id='store', data=df_init.to_dict('records')),
    dcc.Store(id='alert-store', data=''),
    html.Div(id='banner'),
    html.Div(className='kpis', children=[
        kpi('k-recus', 'Emails reçus'), kpi('k-envoyes', 'Emails envoyés'),
        kpi('k-reclam', 'Réclamations reçues'), kpi('k-ventes', 'Emails de vente envoyés'),
        kpi('k-cmd', 'Commandes cette heure')]),

    html.Div(className='row', children=[
        html.Div(className='card', style={'flex': 2, 'minWidth': 420}, children=[
            html.H3('Tendance des emails'),
            dcc.RadioItems(id='gran', value='h', inline=True, labelStyle={'marginRight': 20},
                           options=[{'label': ' Par heure (48 h)', 'value': 'h'},
                                    {'label': ' Par jour (7 j)', 'value': 'D'}]),
            dcc.Graph(id='trend'),
            dcc.Graph(id='bar-cat'),
        ]),
        html.Div(className='card', style={'flex': 1, 'minWidth': 280}, children=[
            html.H3("Seuil d'urgence (commandes / heure)"),
            dcc.Slider(id='seuil', min=1, max=20, step=1, value=5,
                       marks={1: '1', 5: '5', 10: '10', 15: '15', 20: '20'},
                       tooltip={'placement': 'bottom'}),
            html.H3('Simulation'),
            html.Button('+1 réclamation', id='b-reclam', n_clicks=0),
            html.Button('+1 commande', id='b-cmd', n_clicks=0),
            html.Button('+8 commandes (rafale)', id='b-burst', n_clicks=0),
            html.H3('Envoyer un email'),
            dcc.Input(id='to', type='email', placeholder='destinataire@mail.com', style={'width': '100%'}),
            dcc.Input(id='subject', type='text', placeholder='Objet', style={'width': '100%', 'marginTop': 6}),
            dcc.Textarea(id='body', placeholder='Message...', style={'width': '100%', 'marginTop': 6, 'height': 70}),
            dcc.Dropdown(id='cat-send', options=['vente', 'support'], value='vente', clearable=False,
                         style={'marginTop': 6}),
            html.Button('Envoyer', id='b-send', n_clicks=0),
            html.Div(id='status', style={'marginTop': 8, 'fontSize': 13}),
        ]),
    ]),

    html.H3('5 derniers emails'),
    html.Div(className='card', children=[
        html.Div(style={'display': 'flex', 'gap': 16, 'flexWrap': 'wrap', 'marginBottom': 10}, children=[
            dcc.Dropdown(id='f-cat', options=CATEGORIES, value=CATEGORIES, multi=True,
                         style={'minWidth': 320}),
            dcc.Input(id='f-mot', type='text', placeholder='Mot-clé / expression régulière'),
            dcc.Checklist(id='f-nonlu', options=[{'label': ' Non lus seulement', 'value': 'nonlu'}], value=[]),
        ]),
        dash_table.DataTable(
            id='table',
            columns=[{'name': n, 'id': i} for i, n in [('Date', 'Date'), ('direction', 'Sens'),
                                                       ('categorie', 'Catégorie'), ('contact', 'Contact'),
                                                       ('sujet', 'Objet'), ('lu', 'Lu')]],
            style_header={'fontWeight': 'bold', 'backgroundColor': '#147bff', 'color': 'white'},
            style_cell={'textAlign': 'left', 'padding': 8},
            style_data_conditional=[
                {'if': {'filter_query': '{categorie} = "alerte"'}, 'backgroundColor': '#ffe3e3'},
                {'if': {'filter_query': '{categorie} = "réclamation"'}, 'backgroundColor': '#fff4e0'}]),
    ]),
])


# 4. Callback 1 : actions utilisateur (fonction pure : lit les State, renvoie les nouvelles données)
@app.callback(
    Output('store', 'data'), Output('alert-store', 'data'), Output('status', 'children'),
    Input('b-reclam', 'n_clicks'), Input('b-cmd', 'n_clicks'),
    Input('b-burst', 'n_clicks'), Input('b-send', 'n_clicks'),
    State('store', 'data'), State('alert-store', 'data'), State('seuil', 'value'),
    State('to', 'value'), State('subject', 'value'), State('body', 'value'), State('cat-send', 'value'),
    prevent_initial_call=True)
def actions(_r, _c, _b, _s, records, alert_hour, seuil, to, subject, body, cat_send):
    trigger = callback_context.triggered_id
    records = list(records)
    messages = []

    if trigger == 'b-reclam':
        records.append(creer_email_fictif('reçu', 'réclamation'))
        messages.append('Réclamation reçue (simulée).')
    elif trigger == 'b-cmd':
        records.append(creer_email_fictif('reçu', 'commande'))
        messages.append('Commande reçue (simulée).')
    elif trigger == 'b-burst':
        records += [creer_email_fictif('reçu', 'commande') for _ in range(8)]
        messages.append('8 commandes reçues (simulées).')
    elif trigger == 'b-send':
        if not to or not subject:
            return records, alert_hour, '⚠️ Renseignez le destinataire et l\'objet.'
        res = send_email(subject, body or '', to)
        rec = creer_email_fictif('envoyé', cat_send)
        rec.update(contact=to, sujet=subject)
        records.append(rec)
        messages.append(f'Email {res} à {to}.')

    records, alert_hour, msg = alert_system(records, seuil or 5, alert_hour)
    if msg:
        messages.append(msg)
    return records, alert_hour, ' '.join(messages)


# 5. Callback 2 : mise à jour de l'affichage (Pandas filtre/agrège AVANT Plotly - diapo 35)
@app.callback(
    Output('k-recus', 'children'), Output('k-envoyes', 'children'), Output('k-reclam', 'children'),
    Output('k-ventes', 'children'), Output('k-cmd', 'children'), Output('banner', 'children'),
    Output('trend', 'figure'), Output('bar-cat', 'figure'), Output('table', 'data'),
    Input('store', 'data'), Input('gran', 'value'), Input('seuil', 'value'),
    Input('f-cat', 'value'), Input('f-mot', 'value'), Input('f-nonlu', 'value'))
def render(records, gran, seuil, f_cat, f_mot, f_nonlu):
    df = prepare_data(records)
    seuil = seuil or 5
    recus = df[df.direction == 'reçu']
    envoyes = df[df.direction == 'envoyé']
    n_cmd = commandes_heure(records)

    if n_cmd > seuil:
        banner = html.Div(f"🚨 CAS D'URGENCE : {n_cmd} commandes cette heure (seuil {seuil}) - alerte envoyée.",
                          className='banner banner-alert')
    else:
        banner = html.Div(f'✅ Situation normale : {n_cmd} commande(s) cette heure (seuil {seuil}).',
                          className='banner banner-ok')

    # Tendance : Line Chart pour les séries temporelles (diapo 28)
    depuis = pd.Timestamp.now() - (pd.Timedelta(hours=48) if gran == 'h' else pd.Timedelta(days=7))
    sub = df[df.Date >= depuis].copy()
    sub['periode'] = sub.Date.dt.floor(gran)
    agg = sub.groupby(['periode', 'direction']).size().reset_index(name='emails')
    fig = px.line(agg, x='periode', y='emails', color='direction', markers=True,
                  color_discrete_map={'reçu': '#147bff', 'envoyé': '#e76f51'}, template='plotly_white')
    fig.update_layout(title='Emails reçus / envoyés', xaxis_title=None, yaxis_title="Nombre d'emails",
                      legend_title=None, margin=dict(t=40, b=20))

    # Comparaison catégorielle : Bar Chart, axe à zéro (diapo 27-28)
    par_cat = df.groupby('categorie').size().reset_index(name='emails')
    fig_cat = px.bar(par_cat, x='categorie', y='emails', template='plotly_white')
    fig_cat.update_traces(marker_color='#147bff', hovertemplate='%{x} : %{y} emails')
    fig_cat.update_layout(title='Emails par catégorie', xaxis_title=None, yaxis_title="Nombre d'emails",
                          margin=dict(t=40, b=20))

    # Filtrage avancé : catégorie + mot-clé/regex + non lus (diapo 18)
    t = df[df.categorie.isin(f_cat or [])]
    if f_mot:
        try:
            t = t[t.sujet.str.contains(f_mot, flags=re.IGNORECASE, regex=True)]
        except re.error:
            pass
    if f_nonlu:
        t = t[~t.lu]
    last5 = t.sort_values('Date', ascending=False).head(5).copy()
    last5['Date'] = last5.Date.dt.strftime('%d/%m %H:%M')
    last5['lu'] = last5.lu.map({True: 'oui', False: 'non'})

    return (len(recus), len(envoyes), int((recus.categorie == 'réclamation').sum()),
            int((envoyes.categorie == 'vente').sum()), n_cmd, banner, fig, fig_cat, last5.to_dict('records'))


# 6. Lancement du serveur (diapo 34)
if __name__ == '__main__':
    app.run_server(debug=True)
