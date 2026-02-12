from __future__ import annotations

import holidays
import openmeteo_requests
import pandas as pd
import requests
import requests_cache
from retry_requests import retry
from psycopg2.extras import execute_batch

from connexion import ConnexionBDD


ELECTRICITY_API_URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-metropoles-tr/exports/json"
WEATHER_API_URL = "https://archive-api.open-meteo.com/v1/archive"


# ==============================
# EXTRACTION
# ==============================

def fetch_brest_electricity_data() -> pd.DataFrame:
    params = {
        "where": "libelle_metropole='Brest Métropole' AND date_heure >= '2020-01-01' AND date_heure <= '2025-12-31'",
        "order_by": "date_heure ASC",
        "timezone": "UTC",
    }

    response = requests.get(ELECTRICITY_API_URL, params=params, timeout=30)
    response.raise_for_status()
    df = pd.DataFrame(response.json())
    return df[["date_heure", "consommation"]].dropna()


def get_weather_data_brest(start_date: str, end_date: str) -> pd.DataFrame:
    cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    params = {
        "latitude": 48.3904,
        "longitude": -4.4861,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "shortwave_radiation"],
        "timezone": "Europe/Berlin",
    }

    response = openmeteo.weather_api(WEATHER_API_URL, params=params)[0]
    hourly = response.Hourly()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        ),
        "temperature": hourly.Variables(0).ValuesAsNumpy(),
        "humidite": hourly.Variables(1).ValuesAsNumpy(),
        "vent": hourly.Variables(2).ValuesAsNumpy(),
        "rayonnement": hourly.Variables(3).ValuesAsNumpy(),
    }

    return pd.DataFrame(hourly_data).resample("D", on="date").mean()


# ==============================
# TRANSFORMATION
# ==============================

def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    fr_holidays = holidays.France()
    df["jour"] = df.index.dayofweek
    df["mois"] = df.index.month
    df["weekend"] = df.index.dayofweek.isin([5, 6])
    df["vacances"] = df.index.map(lambda x: x in fr_holidays)
    return df


def prepare_data():

    df_conso = fetch_brest_electricity_data()
    df_conso = df_conso.rename(columns={"date_heure": "date"})
    df_conso["date"] = pd.to_datetime(df_conso["date"], utc=True)
    df_conso = df_conso.set_index("date").sort_index()
    df_conso_daily = df_conso["consommation"].resample("D").mean().interpolate()

    df_weather = get_weather_data_brest("2020-01-01", "2025-12-31")

    df = pd.merge(df_conso_daily, df_weather, left_index=True, right_index=True, how="inner")

    df = add_calendar_features(df)
    df["temperature_prev"] = df["temperature"]

    df = df.dropna()

    return df_conso_daily, df


# ==============================
# LOAD OPTIMISÉ
# ==============================

def insert_consumption(df_conso: pd.Series):

    bdd, curseur = ConnexionBDD.connexion()

    records = [
        (date, float(value))
        for date, value in df_conso.items()
    ]

    query = """
        INSERT INTO consommation (date_mesure, consommation_mw)
        VALUES (%s, %s)
        ON CONFLICT (date_mesure) DO NOTHING;
    """

    execute_batch(curseur, query, records, page_size=1000)
    bdd.commit()


def insert_mesures(df: pd.DataFrame):

    bdd, curseur = ConnexionBDD.connexion()

    records = [
        (
            index,
            float(row["temperature"]),
            float(row["humidite"]),
            float(row["vent"]),
            float(row["rayonnement"]),
            float(row["temperature_prev"]),
            int(row["jour"]),
            int(row["mois"]),
            bool(row["weekend"]),
            bool(row["vacances"]),
        )
        for index, row in df.iterrows()
    ]

    query = """
        INSERT INTO mesures (
            date_mesure,
            temperature,
            humidite,
            vent,
            rayonnement,
            temperature_prev,
            jour,
            mois,
            weekend,
            vacances
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (date_mesure) DO NOTHING;
    """

    execute_batch(curseur, query, records, page_size=1000)
    bdd.commit()


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":

    print("Extraction et transformation...")
    df_conso, df_full = prepare_data()

    print("Insertion consommation (batch)...")
    insert_consumption(df_conso)

    print("Insertion mesures (batch)...")
    insert_mesures(df_full)

    ConnexionBDD.deconnexion()

    print("ETL terminé (optimisé).")
