import requests
import pandas as pd
import openmeteo_requests
import requests_cache
import holidays
from retry_requests import retry
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

# consommation d'électricité à Brest Métropole (2020-2025)
def fetch_brest_electricity_data():
    base_url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-metropoles-tr/exports/json"
    
    # Paramètres de la requête
    params = {
        "where": "libelle_metropole='Brest Métropole' AND date_heure >= '2020-01-01' AND date_heure <= '2025-12-31'",
        "order_by": "date_heure ASC",
        "timezone": "UTC"
    }
    
    print("Récupération des données pour Brest Métropole (2020-2025)...")
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data)            
        df = df[['date_heure', 'consommation']].dropna()
        
        return df

    except Exception as e:
        print(f"Erreur lors de la récupération : {e}")
        return None


df_conso_brest = fetch_brest_electricity_data()

if df_conso_brest is not None:
    # Sauvegarde pour l'atelier
    df_conso_brest.to_csv("conso_brest_2020_2025.csv", index=False)

# 1. indexation temporelle
df_conso_brest = df_conso_brest.rename(columns={"date_heure": "date"})
df_conso_brest['date'] = pd.to_datetime(df_conso_brest['date'], utc=True)
df_conso_brest = df_conso_brest.set_index('date').sort_index()

# météo
# changement de temporalité des données
df_conso_brest_journ = df_conso_brest['consommation'].resample('D').mean().interpolate()

# Configuration de l'API avec cache et relance automatique en cas d'erreur
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def get_weather_data_brest(start_date, end_date):
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": 48.3904, # Brest
        "longitude": -4.4861,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "shortwave_radiation"],
        "timezone": "Europe/Berlin"
    }
    
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Processus de transformation des données horaires
    hourly = response.Hourly()
    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}
    
    hourly_data["temp_moy"] = hourly.Variables(0).ValuesAsNumpy()
    hourly_data["humidity"] = hourly.Variables(1).ValuesAsNumpy()
    hourly_data["vent_vitesse"] = hourly.Variables(2).ValuesAsNumpy()
    hourly_data["rayonnement_moyen"] = hourly.Variables(3).ValuesAsNumpy()

    df_meteo = pd.DataFrame(data=hourly_data)
    
    # Passage en format journalier
    df_meteo_journ = df_meteo.resample('D', on='date').mean()
    
    return df_meteo_journ

df_meteo_brest_journ = get_weather_data_brest("2020-01-01", "2025-12-31")

# 2. Fusion (Jointure sur la date)
df_data_multi_brest = pd.merge(df_conso_brest_journ, df_meteo_brest_journ, on='date', how='inner')
print(df_data_multi_brest.head())

# --- PASSÉ (Lags) ---
# Consommation de la veille (J-1), de l'avant veille (J-2) et de la semaine dernière (J-7) pour la saisonnalité
df_data_multi_brest['conso_obs_j-1'] = df_data_multi_brest['consommation'].shift(1)
df_data_multi_brest['conso_obs_j-2'] = df_data_multi_brest['consommation'].shift(2)
df_data_multi_brest['conso_obs_j-7'] = df_data_multi_brest['consommation'].shift(7)

# Météo observée hier (J-1) pour l'inertie thermique
df_data_multi_brest['temp_obs_j-1'] = df_data_multi_brest['temp_moy'].shift(1)

# Météo observée hier (J-1) pour l'humidité
df_data_multi_brest['humidity_j-1'] = df_data_multi_brest['humidity'].shift(1)

# Météo observée hier (J-1) pour le rayonnement
df_data_multi_brest['rayonnement_moyen_j-1'] = df_data_multi_brest['rayonnement_moyen'].shift(1)

# Météo observée hier (J-1) pour le vent
df_data_multi_brest['vent_vitesse_j-1'] = df_data_multi_brest['vent_vitesse'].shift(1)

# --- FUTUR / PRÉVISIONS (Leads) ---
# On utilise la donnée réelle de J comme si c'était la prévision faite le matin même
df_data_multi_brest['temp_prev_j'] = df_data_multi_brest['temp_moy'] 

# On utilise la donnée de J+1 comme prévision pour demain (Lead)
df_data_multi_brest['temp_prev_j+1'] = df_data_multi_brest['temp_moy'].shift(-1)

df_data_multi_brest = df_data_multi_brest.dropna()

fr_holidays = holidays.France()

def add_calendar_features(df):
    
    df_enriched = df.copy()
    
    # 1. Variables temporelles basiques
    df_enriched['day_of_week'] = df_enriched.index.dayofweek
    df_enriched['month'] = df_enriched.index.month
    df_enriched['is_weekend'] = df_enriched.index.dayofweek.isin([5, 6]).astype(int)
    
    # 2. Jours fériés (Boolean : 1 si férié, 0 sinon)
    df_enriched['is_holiday'] = df_enriched.index.map(lambda x: 1 if x in fr_holidays else 0)
    
    # 3. Optionnel : Veille et Lendemain de jour férié (souvent utile pour les ponts)
    df_enriched['is_holiday_prev'] = df_enriched['is_holiday'].shift(-1, fill_value=0)
    df_enriched['is_holiday_next'] = df_enriched['is_holiday'].shift(1, fill_value=0)
    
    return df_enriched

df_data_multi_brest = add_calendar_features(df_data_multi_brest)

dataset_train = df_data_multi_brest['2015-01-01':'2024-12-31']
dataset_test = df_data_multi_brest['2025-01-01':'2025-12-31']

# 1. Normalisation
scaler_uni = MinMaxScaler(feature_range=(0, 1))
scaler_multi_x = MinMaxScaler(feature_range=(0, 1))
scaler_multi_y = MinMaxScaler(feature_range=(0, 1))

# Sélection des colonnes pour le modèle
features = [
    'conso_obs_j-1','conso_obs_j-2', 'conso_obs_j-7', 
    'temp_moy',   'humidity',  'vent_vitesse', 'rayonnement_moyen',
    'temp_obs_j-1',  'humidity_j-1', 'rayonnement_moyen_j-1', 'rayonnement_moyen_j-1','vent_vitesse_j-1',
    'temp_prev_j',  'temp_prev_j+1',
    'day_of_week','month','is_weekend','is_holiday','is_holiday_prev','is_holiday_next'
]
target = 'consommation'

X_train_multi = dataset_train[features].values
y_train_multi = dataset_train[target].values

X_test_multi = dataset_test[features].values
y_test_multi = dataset_test[target].values

X_train_multi_scaled = scaler_multi_x.fit_transform(X_train_multi)
X_test_multi_scaled = scaler_multi_x.transform(X_test_multi)
y_train_multi_scaled = scaler_multi_y.fit_transform(y_train_multi.reshape(-1, 1))
y_test_multi_scaled = scaler_multi_y.transform(y_test_multi.reshape(-1, 1))

def create_sequences_for_multivariate(X, y, window_size):
    X_seq, y_seq = [], []
    for i in range(window_size, len(X)):
        # On prend une fenêtre de 'window_size' jours pour X
        X_seq.append(X[i-window_size:i])
        # La cible est la valeur de y juste après cette fenêtre
        y_seq.append(y[i])
    return np.array(X_seq), np.array(y_seq)

#Paramètre critique : quelle longueur d'historicité nous voulons ? Ici ce paramètre est réglé à 30, mais c'est potentiellement beaucoup trop long
window_size = 30 

X_train_multi_scaled_seq, y_train_multi_scaled_seq = create_sequences_for_multivariate(X_train_multi_scaled, y_train_multi_scaled, window_size)
X_test_multi_scaled_seq, y_test_multi_scaled_seq = create_sequences_for_multivariate(X_test_multi_scaled, y_test_multi_scaled, window_size)

# Initialisation du modèle
model_lstm_multi = Sequential([
   
    # input_shape = (nb_pas_de_temps, nb_features)
    LSTM(50, activation='relu', input_shape=(window_size, X_train_multi_scaled_seq.shape[2]), return_sequences=False),
    
    
    # Dropout pour éviter le sur-apprentissage (overfitting)
    Dropout(0.2),   
    
    # Couche de sortie : 1 neurone pour la prédiction finale (valeur continue)
    Dense(1)
])

# Compilation
model_lstm_multi.compile(optimizer='adam', loss='mean_squared_error')

early_stop = EarlyStopping(monitor='val_loss', patience=30, restore_best_weights=True)
# 3. Entraînement
# epochs : nombre de passages sur les données
# batch_size : nombre d'échantillons traités avant la mise à jour des poids
history = model_lstm_multi.fit(
    #X_train_multi_scaled_seq[:,:,0], y_train_multi_scaled_seq, 
    X_train_multi_scaled_seq,y_train_multi_scaled_seq,
    epochs=1000, 
    batch_size=32, 
    validation_split=0.1, # On garde 10% pour valider pendant l'entraînement
    callbacks=[early_stop],
    verbose=1
)

# 1. Prédictions
predictions_scaled = model_lstm_multi.predict(X_test_multi_scaled_seq)

# 2. Dénormalisation des prédictions
y_pred = scaler_multi_y.inverse_transform(predictions_scaled)
y_actual = scaler_multi_y.inverse_transform(y_test_multi_scaled_seq)

# 1. MAE : Mean Absolute Error (Erreur Absolue Moyenne)
mae = mean_absolute_error(y_actual, y_pred)

# 2. RMSE : Root Mean Squared Error (Erreur Quadratique Moyenne)
rmse = np.sqrt(mean_squared_error(y_actual, y_pred))

# 3. MAPE : Mean Absolute Percentage Error (Erreur en Pourcentage)
mape = np.mean(np.abs((y_actual - y_pred) / y_actual)) * 100