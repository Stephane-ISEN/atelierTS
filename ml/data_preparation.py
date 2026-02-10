from __future__ import annotations

import holidays
import openmeteo_requests
import pandas as pd
import requests
import requests_cache
from retry_requests import retry

ELECTRICITY_API_URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-metropoles-tr/exports/json"
WEATHER_API_URL = "https://archive-api.open-meteo.com/v1/archive"

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
TARGET = "consommation"


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
        "temp_moy": hourly.Variables(0).ValuesAsNumpy(),
        "humidity": hourly.Variables(1).ValuesAsNumpy(),
        "vent_vitesse": hourly.Variables(2).ValuesAsNumpy(),
        "rayonnement_moyen": hourly.Variables(3).ValuesAsNumpy(),
    }

    return pd.DataFrame(hourly_data).resample("D", on="date").mean()


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    fr_holidays = holidays.France()
    df_enriched = df.copy()
    df_enriched["day_of_week"] = df_enriched.index.dayofweek
    df_enriched["month"] = df_enriched.index.month
    df_enriched["is_weekend"] = df_enriched.index.dayofweek.isin([5, 6]).astype(int)
    df_enriched["is_holiday"] = df_enriched.index.map(lambda x: 1 if x in fr_holidays else 0)
    df_enriched["is_holiday_prev"] = df_enriched["is_holiday"].shift(-1, fill_value=0)
    df_enriched["is_holiday_next"] = df_enriched["is_holiday"].shift(1, fill_value=0)
    return df_enriched


def prepare_datasets() -> tuple[pd.DataFrame, pd.DataFrame, list[str], str]:
    df_conso = fetch_brest_electricity_data()
    df_conso.to_csv("conso_brest_2020_2025.csv", index=False)

    df_conso = df_conso.rename(columns={"date_heure": "date"})
    df_conso["date"] = pd.to_datetime(df_conso["date"], utc=True)
    df_conso = df_conso.set_index("date").sort_index()
    df_conso_daily = df_conso["consommation"].resample("D").mean().interpolate()

    df_weather_daily = get_weather_data_brest("2020-01-01", "2025-12-31")
    df = pd.merge(df_conso_daily, df_weather_daily, on="date", how="inner")

    df["conso_obs_j-1"] = df["consommation"].shift(1)
    df["conso_obs_j-2"] = df["consommation"].shift(2)
    df["conso_obs_j-7"] = df["consommation"].shift(7)
    df["temp_obs_j-1"] = df["temp_moy"].shift(1)
    df["humidity_j-1"] = df["humidity"].shift(1)
    df["rayonnement_moyen_j-1"] = df["rayonnement_moyen"].shift(1)
    df["vent_vitesse_j-1"] = df["vent_vitesse"].shift(1)
    df["temp_prev_j"] = df["temp_moy"]
    df["temp_prev_j+1"] = df["temp_moy"].shift(-1)

    df = add_calendar_features(df).dropna()
    dataset_train = df["2020-01-01":"2024-12-31"]
    dataset_test = df["2025-01-01":"2025-12-31"]

    return dataset_train, dataset_test, FEATURES, TARGET
