from fastapi import FastAPI
from datetime import date
import mlflow.keras
import numpy as np

app = FastAPI()

# ⚠️ Adapter le chemin réel
MODEL_PATH = "./mlruns/artifacts/1/efb60fb923414fac95bc3f4c72a5d073/artifacts/model"  # chemin vers le modèle enregistré par mlflow

model = mlflow.keras.load_model(MODEL_PATH)

FEATURES = 19  # nombre de features
WINDOW_SIZE = 30


@app.get("/predict")
def predict(d: date):

    # 19 valeurs en dur (ordre identique à l'entraînement)
    base_values = [
        1200, 1180, 1250,
        12.5, 75, 15, 200,
        11.8, 78, 180, 12,
        13.0, 14.0,
        2, 2,
        0, 0, 0, 0
    ]

    # On répète ces valeurs 30 fois pour simuler une séquence LSTM
    sequence = [base_values for _ in range(WINDOW_SIZE)]

    # Shape attendue par LSTM : (batch, time_steps, features)
    X = np.array([sequence])   # => (1, 30, 19)

    prediction = model.predict(X)

    # prediction est souvent shape (1,1)
    y_pred = float(prediction[0][0])

    return {"date": d, "prediction": y_pred}
