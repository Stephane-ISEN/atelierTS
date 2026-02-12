# Série temporelle consommation d'énergie

Projet de prévision de consommation électrique (Brest Métropole) avec un modèle **LSTM multivarié** et un service via **FastAPI**.

---

# Créer la structure

À la racine de ton projet :

```
project/
├── api/
│   └── main.py
├── mlruns/
└── ...
```

Créer le dossier :

```bash
mkdir api
touch api/main.py
```

---

# Rappel : comment MLflow sauvegarde un modèle

Quand tu fais :

```python
mlflow.keras.log_model(model, artifact_path="model")
```

MLflow crée un dossier :

```
mlruns/<experiment_id>/<run_id>/artifacts/model/
```

Ce dossier contient :

* MLmodel
* model.keras (ou SavedModel)
* requirements.txt
* python_env.yaml

---

# Charger le modèle

On utilise :

```python
mlflow.keras.load_model(path)
```

`path` doit pointer vers le dossier `model`.

Exemple :

```python
../mlruns/1/<RUN_ID>/artifacts/model
```

---

# Rappel : template d’un endpoint FastAPI

```python
@app.get("/route")
def fonction(param: type):
    return {"clé": "valeur"}
```

* `@app.get()` → méthode HTTP
* `"/route"` → URL
* paramètres typés
* retour JSON automatique

---

# Rappel format des features

Ton modèle LSTM attend :

```
(batch_size, window_size, n_features)
```

Dans ton cas :

```
(1, 30, 19)
```

* 1 → un seul exemple
* 30 → fenêtre temporelle
* 19 → nombre de variables

---

# Lancer l’API

À la racine du projet :

```bash
uv run uvicorn api.main:app --reload
```

Tu dois voir :

```
Uvicorn running on http://127.0.0.1:8000
```

---

# Tester l’API

Ouvre :

```
http://127.0.0.1:8000/docs
```

Interface Swagger automatique.

---

# 📥 Format attendu de la donnée

Le endpoint attend :

```
/predict?d=YYYY-MM-DD
```

Exemple :

```
http://127.0.0.1:8000/predict?d=2026-02-12
```
