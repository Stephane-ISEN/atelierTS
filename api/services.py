from datetime import date, timedelta
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

    # Requête SQL :
    # - Jointure consommation + mesures
    # - Filtre sur la fenêtre temporelle
    # - Tri chronologique croissant


  
    # Vérification : on doit avoir exactement 30 jours


  
    # Construction de la séquence jour par jour
    for i in range(len(rows)):

        # Décomposition de la ligne SQL
  
        # ==========================
        # Création des décalages temporels
        # ==========================

        # Consommation J-1, J-2, J-7
        # Si on est au début de la fenêtre, on utilise la valeur courante

      
        # Variables météo décalées à J-1


      
        # ==========================
        # Variables calendaires
        # ==========================


        # Simplification actuelle :
        # on ne calcule pas encore les vrais décalages holiday

      
        # ==========================
        # Construction du vecteur features
        # ==========================


    # On garde strictement les 30 derniers jours

      
    # Transformation en tenseur numpy :
    X = np.array([sequence])

    return X
