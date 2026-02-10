from __future__ import annotations

from bdd.connexion import ConnexionBDD
from ml.data_preparation import fetch_brest_electricity_data, get_weather_data_brest


def charger_consommation(cursor):
    df_conso = fetch_brest_electricity_data().rename(columns={"date_heure": "date_mesure", "consommation": "consommation_mw"})
    df_conso["date_mesure"] = df_conso["date_mesure"].astype(str)

    for row in df_conso.itertuples(index=False):
        cursor.execute(
            """
            INSERT INTO consommation (date_mesure, consommation_mw)
            VALUES (%s, %s)
            ON CONFLICT (date_mesure) DO UPDATE
            SET consommation_mw = EXCLUDED.consommation_mw
            """,
            (row.date_mesure, float(row.consommation_mw)),
        )


def charger_meteo(cursor):
    df_meteo = get_weather_data_brest("2020-01-01", "2025-12-31").reset_index()
    df_meteo = df_meteo.rename(
        columns={
            "date": "date_mesure",
            "temp_moy": "temperature_moyenne",
            "humidity": "humidite_relative",
            "vent_vitesse": "vitesse_vent",
        }
    )
    df_meteo["date_mesure"] = df_meteo["date_mesure"].astype(str)

    for row in df_meteo.itertuples(index=False):
        cursor.execute(
            """
            INSERT INTO meteo (
                date_mesure,
                temperature_moyenne,
                humidite_relative,
                vitesse_vent,
                rayonnement_moyen
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (date_mesure) DO UPDATE
            SET
                temperature_moyenne = EXCLUDED.temperature_moyenne,
                humidite_relative = EXCLUDED.humidite_relative,
                vitesse_vent = EXCLUDED.vitesse_vent,
                rayonnement_moyen = EXCLUDED.rayonnement_moyen
            """,
            (
                row.date_mesure,
                float(row.temperature_moyenne),
                float(row.humidite_relative),
                float(row.vitesse_vent),
                float(row.rayonnement_moyen),
            ),
        )


def charger_prediction_baseline(cursor):
    cursor.execute(
        """
        INSERT INTO prediction (date_prediction, valeur_reelle, valeur_predite, modele)
        SELECT
            c.date_mesure AS date_prediction,
            c.consommation_mw AS valeur_reelle,
            LAG(c.consommation_mw, 1) OVER (ORDER BY c.date_mesure) AS valeur_predite,
            'baseline_j-1' AS modele
        FROM consommation c
        ON CONFLICT (date_prediction, modele) DO UPDATE
        SET
            valeur_reelle = EXCLUDED.valeur_reelle,
            valeur_predite = EXCLUDED.valeur_predite
        """
    )


def executer_etl():
    bdd, curseur = ConnexionBDD.connexion()
    try:
        charger_consommation(curseur)
        charger_meteo(curseur)
        charger_prediction_baseline(curseur)
        bdd.commit()
        print("ETL terminé : tables consommation, meteo et prediction alimentées.")
    except Exception:
        bdd.rollback()
        raise
    finally:
        ConnexionBDD.deconnexion()


if __name__ == "__main__":
    executer_etl()
