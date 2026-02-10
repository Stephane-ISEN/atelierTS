# atelierTS

Projet de prévision de consommation électrique (Brest Métropole) avec un modèle **LSTM multivarié**, un suivi d'expériences via **MLflow** et une base **TimescaleDB (PostgreSQL)**.

---

## 1) Organisation du code Python (3 fichiers)

Le code de `ml/modele.py` a été factorisé en 3 modules pour séparer clairement les responsabilités.

### `ml/data_preparation.py`
Préparation des données : récupération conso/météo, agrégation journalière, features temporelles/calendaires, split train/test.

### `ml/model_preparation.py`
Préparation ML : normalisation (`MinMaxScaler`), création des séquences (`window_size`), modèle LSTM, entraînement et métriques (MAE/RMSE/MAPE).

### `ml/modele.py`
Orchestration : enchaîne data + modèle, configure MLflow et lance un run d'entraînement complet.

---

## 2) Lignes MLflow ajoutées dans Python

Dans `ml/modele.py` :
- `mlflow.set_tracking_uri(...)` : définit où sont stockés les runs.
- `mlflow.set_experiment("brest_consumption_forecast")` : regroupe les runs dans une expérience.
- `with mlflow.start_run(...)` : crée un run d'entraînement.
- `mlflow.log_params(...)` : journalise les hyperparamètres.
- `mlflow.log_metric(...)` / `mlflow.log_metrics(...)` : journalise les performances.
- `mlflow.keras.log_model(...)` : enregistre le modèle entraîné comme artefact.

---

## 3) Docker Compose (MLflow + TimescaleDB)

Le `docker-compose.yml` lance 2 services :

- **mlflow**
  - UI sur `http://localhost:5000`
  - backend SQLite dans `./mlflow`

- **timescaledb**
  - image `timescale/timescaledb:latest-pg17`
  - PostgreSQL exposé sur `localhost:5432`
  - variables lues depuis `.env`
  - volumes :
    - `./data/init.sql:/docker-entrypoint-initdb.d/init.sql` (initialisation des tables)
    - `./data/postgresql:/var/lib/postgresql/data` (persistance locale)

---

## 4) Base TimescaleDB : schéma et ETL

## Fichier d'initialisation SQL
`data/init.sql` crée :
- `consommation`
- `meteo`
- `prediction`

et transforme ces tables en hypertables Timescale.

## Scripts Python BDD
- `bdd/connexion.py` : classe `ConnexionBDD`
  - variables de classe `bdd` et `curseur`
  - méthodes de classe `connexion()` et `deconnexion()`
  - lit les variables PostgreSQL depuis `.env`
- `bdd/etl.py` : charge les données utiles au modèle dans les 3 tables
  - insertion/upsert de la consommation
  - insertion/upsert de la météo
  - alimentation de `prediction` avec un baseline `J-1`

---

## 5) Lancer l'application web MLflow et ce qu'on doit y trouver

## Prérequis
- Docker + Docker Compose
- `uv`

## Étapes

### A. Préparer l'environnement Python
```bash
uv sync
```

### B. Créer le fichier `.env`
Exemple minimal (à adapter) :
```env
POSTGRES_HOST=timescaledb
POSTGRES_PORT=5432
POSTGRES_DB=atelierts
POSTGRES_USER=atelierts
POSTGRES_PASSWORD=atelierts
```

### C. Démarrer les services
```bash
docker compose up -d
```

### D. Charger les données dans la base
```bash
uv run python bdd/etl.py
```

### E. Lancer l'entraînement avec MLflow
```bash
MLFLOW_TRACKING_URI=http://localhost:5000 uv run python ml/modele.py
```

### F. Ouvrir l'UI
- http://localhost:5000

## Ce que vous devriez voir dans MLflow
- expérience **`brest_consumption_forecast`**
- run **`lstm_brest_consumption`**
- paramètres (`window_size`, `epochs`, `batch_size`, `n_features`)
- métriques (`val_loss`, `mae`, `rmse`, `mape`)
- artefact modèle (`model`)

---

## Commandes utiles

```bash
docker compose ps
docker compose logs -f timescaledb
docker compose logs -f mlflow
docker compose down
```
