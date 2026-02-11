# Série temporelle – Prévision de consommation d'énergie (Brest Métropole)

Projet complet de **prévision de consommation électrique** à l’aide d’un modèle **LSTM multivarié** avec suivi des expériences via **MLflow**.

Objectifs :

* Structurer un modèle prêt pour la production
* Versionner les entraînements
* Suivre les métriques
* Sauvegarder les modèles entraînés

---

# 1) Préparer le modèle pour la production

## 🎯 Objectif

Passer d’un notebook expérimental à un script structuré, réutilisable et exécutable en ligne de commande.

Un notebook est utile pour explorer.
Un script Python est indispensable pour :

* automatiser l'entraînement
* intégrer MLflow
* dockeriser plus tard
* industrialiser le pipeline

---

## 📁 Étape

Dans le répertoire `./ml`, créer un fichier :

```
ml/modele.py
```

Y déplacer le code du notebook `notebook_2_TS_multivarie` :

* préparation des données
* création des séquences temporelles
* définition du modèle LSTM
* entraînement
* évaluation

---

## 🧠 Bonne pratique

Séparer le code en fonctions :

```python
prepare_datasets()
prepare_training_tensors()
build_lstm_model()
train_and_evaluate()
run_training()
```

Cela permet :

* une meilleure lisibilité
* des tests unitaires
* une réutilisation future (API, batch, etc.)

---

# 2) Lancer MLflow

## 🎯 Objectif

Mettre en place un serveur de suivi des expériences.

MLflow permet de :

* enregistrer les hyperparamètres
* stocker les métriques
* sauvegarder les modèles
* comparer les runs

---

## 📁 Créer la structure locale

À la racine du projet :

```bash
mkdir -p mlruns
```

Cette structure contiendra :

```
mlruns/
├── mlflow.db         ← base SQLite (tracking)
└── 1/                ← numéro de run
```

---

## 🚀 Lancer le serveur MLflow

```bash
uv run mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri sqlite:///mlruns/mlflow.db \
  --default-artifact-root ./mlruns
```

### 🔎 Explication des options

| Option                    | Rôle                                         |
| ------------------------- | -------------------------------------------- |
| `--backend-store-uri`     | Base SQLite qui stocke les runs et métriques |
| `--default-artifact-root` | Dossier où seront stockés les modèles        |
| `--host`                  | Permet d'accéder depuis navigateur           |
| `--port`                  | Port d’accès au serveur                      |

---

## 🌐 Accéder à l’interface

Ouvrir :

```
http://127.0.0.1:5000
```

Interface vide au départ — c’est normal.

---

# 3) Intégrer MLflow dans le script Python

Dans `ml/modele.py`, ajouter les éléments suivants.

---

## 🔗 Définir le serveur MLflow

```python
mlflow.set_tracking_uri("http://127.0.0.1:5000")
```

### 🎯 Rôle

Indique à MLflow :

> Où envoyer les runs.

Sans cette ligne, MLflow fonctionnerait en mode local.

---

## 🗂 Définir l’expérience

```python
mlflow.set_experiment("brest_consumption_forecast")
```

### 🎯 Rôle

* Crée l’expérience si elle n’existe pas
* Regroupe tous les entraînements sous un même projet

---

## ▶️ Démarrer un run

```python
with mlflow.start_run(run_name="lstm_brest_consumption"):
```

### 🎯 Rôle

Un run correspond à **un entraînement complet**.

Tout ce qui est loggé dans ce bloc :

* paramètres
* métriques
* artefacts

sera attaché à ce run.

---

## ⚙️ Logger les hyperparamètres

```python
mlflow.log_params({
    "window_size": window_size,
    "epochs": epochs,
    "batch_size": batch_size,
    "n_features": len(features),
})
```

### 🎯 Rôle

Permet de :

* comprendre comment le modèle a été entraîné
* reproduire les résultats
* comparer plusieurs configurations

---

## 📊 Logger les métriques

```python
mlflow.log_metric("val_loss", final_val_loss)
mlflow.log_metrics(metrics)
```

### 🎯 Rôle

Enregistrer les performances :

* `val_loss`
* `mae`
* `rmse`
* `mape`

Permet :

* comparaison visuelle entre runs
* sélection du meilleur modèle

---

## 💾 Sauvegarder le modèle

```python
mlflow.keras.log_model(model, artifact_path="model")
```

### 🎯 Rôle

Enregistre :

* architecture du modèle
* poids entraînés
* configuration

Le modèle est stocké dans :

```
mlruns/artifacts/...
```

Il pourra être :

* rechargé plus tard
* servi via API
* versionné

---

# 4) Lancer l'entraînement

```bash
uv run ml/modele.py
```

### 🎯 Ce qu’il se passe

1. Chargement des données
2. Création des séquences LSTM
3. Entraînement du modèle
4. Enregistrement dans MLflow
5. Sauvegarde du modèle

---

# 5) Ce que vous devriez voir dans l'interface

Dans MLflow UI :

## 📁 Une expérience

```
brest_consumption_forecast
```

## ▶️ Un run

```
lstm_brest_consumption
```

## 📌 Paramètres

* `window_size`
* `epochs`
* `batch_size`
* `n_features`

## 📈 Métriques

* `val_loss`
* `mae`
* `rmse`
* `mape`

## 📦 Artefact

Un dossier :

```
model/
```

Contenant le modèle LSTM sauvegardé.

---
