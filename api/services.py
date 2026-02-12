from datetime import date, timedelta, datetime
import numpy as np
from bdd.connexion import ConnexionBDD

# Taille de la fenêtre temporelle utilisée par le LSTM
# Le modèle attend 30 jours consécutifs en entrée
WINDOW_SIZE = 30

# Liste des features attendues par le modèle
# L'ordre est IMPORTANT : il doit correspondre exactement
# à celui utilisé lors de l'entraînement du modèle
FEATURES = [
    "conso_obs_j-1",
    "conso_obs_j-2",
    "conso_obs_j-7",
    "temp_moy",
    "humidity",
    "vent_vitesse",
    "rayonnement_moyen",
    "temp_obs_j-1",
    "humidity_j-1",
    "rayonnement_moyen_j-1",
    "vent_vitesse_j-1",
    "temp_prev_j",
    "temp_prev_j+1",
    "day_of_week",
    "month",
    "is_weekend",
    "is_holiday",
    "is_holiday_prev",
    "is_holiday_next",
]


def get_features_for_day(target_date: date):
    """
    Construit le tenseur d'entrée du modèle LSTM pour une date donnée.

    Étapes :
    1. Récupérer les 30 jours précédents en base.
    2. Construire les variables décalées (J-1, J-2, J-7, etc.).
    3. Former une séquence de 30 jours.
    4. Retourner un tenseur numpy de forme (1, 30, 19).
    """

    # Ouverture (ou réutilisation) de la connexion à la base
    bdd, curseur = ConnexionBDD.connexion()

    # Détermination de la date de début de la fenêtre
    # On prend les 30 jours précédant la date cible
    start_date = target_date - timedelta(days=WINDOW_SIZE)

    # Requête SQL :
    # - Jointure consommation + mesures
    # - Filtre sur la fenêtre temporelle
    # - Tri chronologique croissant
    curseur.execute(
        """
        SELECT
            c.date_mesure,
            c.consommation_mw,
            m.temperature,
            m.humidite,
            m.vent,
            m.rayonnement,
            m.temperature_prev,
            m.jour,
            m.mois,
            m.weekend,
            m.vacances
        FROM consommation c
        JOIN mesures m ON c.date_mesure = m.date_mesure
        WHERE c.date_mesure >= %s AND c.date_mesure < %s
        ORDER BY c.date_mesure ASC
        """,
        (start_date, target_date),
    )

    rows = curseur.fetchall()

    # Vérification : on doit avoir exactement 30 jours
    if len(rows) < WINDOW_SIZE:
        raise ValueError("Pas assez de données pour construire la fenêtre LSTM")

    sequence = []

    # Construction de la séquence jour par jour
    for i in range(len(rows)):

        # Décomposition de la ligne SQL
        date_i, conso, temp, hum, vent, ray, temp_prev, jour, mois, weekend, vacances = rows[i]

        # ==========================
        # Création des décalages temporels
        # ==========================

        # Consommation J-1, J-2, J-7
        # Si on est au début de la fenêtre, on utilise la valeur courante
        conso_j1 = rows[i - 1][1] if i >= 1 else conso
        conso_j2 = rows[i - 2][1] if i >= 2 else conso
        conso_j7 = rows[i - 7][1] if i >= 7 else conso

        # Variables météo décalées à J-1
        temp_j1 = rows[i - 1][2] if i >= 1 else temp
        hum_j1 = rows[i - 1][3] if i >= 1 else hum
        ray_j1 = rows[i - 1][5] if i >= 1 else ray
        vent_j1 = rows[i - 1][4] if i >= 1 else vent

        # ==========================
        # Variables calendaires
        # ==========================

        day_of_week = jour
        month = mois
        is_weekend = int(weekend)
        is_holiday = int(vacances)

        # Simplification actuelle :
        # on ne calcule pas encore les vrais décalages holiday
        is_holiday_prev = 0
        is_holiday_next = 0

        # ==========================
        # Construction du vecteur features
        # ==========================

        features = [
            conso_j1,
            conso_j2,
            conso_j7,
            temp,
            hum,
            vent,
            ray,
            temp_j1,
            hum_j1,
            ray_j1,
            vent_j1,
            temp_prev,
            temp_prev,  # simplification pour J+1
            day_of_week,
            month,
            is_weekend,
            is_holiday,
            is_holiday_prev,
            is_holiday_next,
        ]

        sequence.append(features)

    # On garde strictement les 30 derniers jours
    sequence = sequence[-WINDOW_SIZE:]

    # Transformation en tenseur numpy :
    # shape = (batch_size=1, time_steps=30, features=19)
    X = np.array([sequence])

    return X

def save_prediction(target_date: datetime, value: float):
    """
    Enregistre la prédiction en base.
    Si une prédiction existe déjà pour cette date,
    on la met à jour.
    """

    bdd, curseur = ConnexionBDD.connexion()

    curseur.execute(
        """
        INSERT INTO prediction (date_prediction, valeur_predite)
        VALUES (%s, %s)
        ON CONFLICT (date_prediction)
        DO UPDATE SET valeur_predite = EXCLUDED.valeur_predite;
        """,
        (target_date, value),
    )

    bdd.commit()
