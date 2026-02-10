# atelierTS

Projet de prévision de consommation électrique (Brest Métropole) avec un modèle **LSTM multivarié** et un suivi d'expériences via **MLflow**.

---

## 1) Organisation du code Python (3 fichiers)

Le code de `ml/modele.py` a été factorisé en 3 modules pour séparer clairement les responsabilités.

### `ml/data_preparation.py`
Responsable de **toute la préparation des données** :
- récupération de la consommation électrique (API Opendatasoft),
- récupération météo (Open-Meteo),
- agrégation journalière,
- fusion des sources,
- création des features temporelles et calendaires,
- split train/test.

En sortie, ce module fournit :
- `dataset_train`,
- `dataset_test`,
- la liste des `features`,
- la `target`.

### `ml/model_preparation.py`
Responsable de la **préparation ML et du modèle** :
- normalisation des variables (`MinMaxScaler`),
- création des séquences temporelles (`window_size`) pour le LSTM,
- construction du modèle Keras (LSTM + Dropout + Dense),
- entraînement,
- calcul des métriques (MAE, RMSE, MAPE).

### `ml/modele.py`
Responsable de l'**orchestration globale** :
- appelle la préparation des données,
- appelle la préparation/entraînement du modèle,
- configure et utilise MLflow,
- lance un run complet reproductible.

Cette séparation rend le projet plus lisible, testable et maintenable.

---

## 2) Lignes MLflow ajoutées dans Python (et à quoi elles servent)

Dans `ml/modele.py`, les blocs MLflow ont un rôle précis :

### `mlflow.set_tracking_uri(...)`
Définit l'URL du serveur MLflow sur lequel écrire les runs.
- Par défaut : `http://127.0.0.1:5000`
- configurable via la variable d'environnement `MLFLOW_TRACKING_URI`

### `mlflow.set_experiment("brest_consumption_forecast")`
Crée/sélectionne l'expérience MLflow qui regroupe les runs de ce projet.

### `with mlflow.start_run(run_name="lstm_brest_consumption"):`
Ouvre un run MLflow (un entraînement complet).
Tout ce qui est loggé dans ce bloc est attaché à ce run.

### `mlflow.log_params({...})`
Enregistre les hyperparamètres utiles à la reproductibilité :
- `window_size`,
- `epochs`,
- `batch_size`,
- `n_features`.

### `mlflow.log_metric("val_loss", ...)` et `mlflow.log_metrics(metrics)`
Enregistre les performances du modèle :
- `val_loss`,
- `mae`,
- `rmse`,
- `mape`.

### `mlflow.keras.log_model(model, artifact_path="model")`
Sauvegarde le modèle entraîné comme artefact MLflow (pour versionner/réutiliser).

---

## 3) Explication du `docker-compose.yml`

Le `docker-compose.yml` fournit un service unique : `mlflow`.

### Ce qu'il configure
- **Image** : `ghcr.io/mlflow/mlflow:v2.22.0`
- **Port** : `5000:5000` (UI accessible depuis l'hôte)
- **Persistance** : volume `./mlflow:/mlflow`
- **Backend store** : SQLite (`/mlflow/mlflow.db`)
- **Artifact store** : `/mlflow/artifacts`

### Pourquoi c'est utile
- démarrage rapide d'un serveur MLflow local,
- conservation des runs/modèles entre redémarrages,
- même configuration pour toute l'équipe.

---

## 4) Lancer l'application web MLflow et ce qu'on doit y trouver

## Prérequis
- Docker + Docker Compose installés
- dépendances Python installées via `uv`

## Étapes

### A. Installer les dépendances Python
```bash
uv sync
```

### B. Démarrer MLflow
```bash
docker compose up -d
```

### C. Vérifier que le service tourne
```bash
docker compose ps
```

### D. Lancer l'entraînement Python
```bash
uv run python ml/modele.py
```

Si besoin, expliciter l'URL du tracking server :
```bash
MLFLOW_TRACKING_URI=http://localhost:5000 uv run python ml/modele.py
```

### E. Ouvrir l'UI MLflow
- URL : http://localhost:5000

## Ce que vous devriez voir dans l'interface
- une expérience nommée **`brest_consumption_forecast`**,
- au moins un run **`lstm_brest_consumption`**,
- les paramètres (`window_size`, `epochs`, `batch_size`, `n_features`),
- les métriques (`val_loss`, `mae`, `rmse`, `mape`),
- un artefact modèle (dossier `model`).

---

## Commandes utiles

### Arrêter MLflow
```bash
docker compose down
```

### Voir les logs MLflow
```bash
docker compose logs -f mlflow
```

### Redémarrer MLflow
```bash
docker compose restart mlflow
```

---

## Structure des fichiers (résumé)

- `ml/data_preparation.py` : ingestion + features + split
- `ml/model_preparation.py` : scalers + séquences + LSTM + évaluation
- `ml/modele.py` : orchestration run + tracking MLflow
- `docker-compose.yml` : serveur MLflow local
