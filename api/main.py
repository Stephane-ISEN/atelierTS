from api.services import get_features_for_day, save_prediction
from fastapi import FastAPI
from datetime import date
import mlflow.keras

app = FastAPI()

# ⚠️ Adapter le chemin réel
MODEL_PATH = "./mlruns/artifacts/1/efb60fb923414fac95bc3f4c72a5d073/artifacts/model"  # chemin vers le modèle enregistré par mlflow

model = mlflow.keras.load_model(MODEL_PATH)

FEATURES = 19  # nombre de features
WINDOW_SIZE = 30


@app.get("/predict")
def predict(d: date):

    X = get_features_for_day(d)

    prediction = model.predict(X)
    y_pred = float(prediction[0][0])

    save_prediction(d, y_pred)

    return {
        "date": d,
        "prediction": y_pred
    }
