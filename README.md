# Série temporelle consommation d'énergie

Projet de prévision de consommation électrique (Brest Métropole).
Intégration  de la base **PostegreSQL** à **FastAPI**.

## Lancer le projet Python (uv)

```bash
uv sync
uv run python ml/modele.py
```

## Lancer MLflow via Docker Compose

```bash
docker compose up -d
```

UI MLflow disponible sur: http://localhost:5000

## Configuration MLflow côté script

Par défaut le script utilise `MLFLOW_TRACKING_URI=http://127.0.0.1:5000`.

Vous pouvez le surcharger:

```bash
MLFLOW_TRACKING_URI=http://localhost:5000 uv run python ml/modele.py
```
