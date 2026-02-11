# Série temporelle consommation d'énergie

## 🛠️ Installation et prise en main du projet

Ce tutoriel vous guide **pas à pas** pour installer l’environnement de travail nécessaire à l’atelier *Time Series & LSTM*, puis pour récupérer et exécuter le projet.

À la fin de cette section, vous aurez :

* un environnement Python propre et reproductible,
* toutes les dépendances installées,
* le projet prêt à être exécuté.

---

### Outils nécessaires

Avant de commencer, deux outils sont indispensables :

**Docker**

Docker permet de lancer facilement les services nécessaires au projet (base de données MySQL, MLflow, etc.) sans configuration complexe.

👉 Téléchargement et installation :

* [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

> 💡 Après l’installation, vérifiez que Docker fonctionne :

```bash
docker --version
```

---

**Visual Studio Code (VS Code)**

VS Code est l’éditeur de code recommandé pour cet atelier.
Il offre une excellente intégration avec Python, Docker et Git.

👉 Téléchargement :

* [https://code.visualstudio.com/](https://code.visualstudio.com/)

Extensions conseillées :

* **Python**
* **Docker**
* **Pylance**
* **Jupiter Notebook**
* **Git**
---

### Installation de `uv` (gestionnaire Python)

Ce projet utilise **uv**, un gestionnaire moderne pour Python, rapide et reproductible.
Il remplace avantageusement `pip` + `venv`.

---

**Installation sur Linux**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

Vérifiez l’installation :

```bash
uv --version
```

---

**Installation sur Windows**

Dans **PowerShell** :

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Vérification :

```powershell
uv --version
```
---

### Récupérer le projet depuis GitHub

Le code source du projet est hébergé sur un dépôt public GitHub.

```bash
git clone https://github.com/Stephane-ISEN/atelierTS.git
cd atelierTS
uv sync
```
---

### Comprendre les fichiers gérés par `uv`

Le projet repose sur trois fichiers clés, qu’il est important de comprendre.

---

`.python-version`

Ce fichier indique la **version exacte de Python** utilisée par le projet.

Exemple :

```
3.12
```

👉 Cela garantit que **tous les participants utilisent la même version de Python**.

---

`pyproject.toml`

C’est le **cœur du projet Python**.
Il contient :

* le nom du projet,
* la version,
* les dépendances,
* les dépendances de développement.

Exemple simplifié :

```toml
[project]
name = "atelier-ts"
version = "0.1.0"
dependencies = [
    "pandas",
    "numpy",
    "fastapi",
]
```

---

`uv.lock`

Ce fichier est généré automatiquement.
Il **fige précisément les versions** de toutes les dépendances.

👉 Il garantit que :

* le projet fonctionne de la même façon sur toutes les machines,
* les installations sont reproductibles.

⚠️ **Ne pas modifier ce fichier à la main.**

---

### Créer un projet avec `uv`

UV permet de créer un projet ainsi :

```bash
uv init AtelierTS
code AtelierTS
```

Cela crée :

* un `pyproject.toml`
* un environnement Python isolé
* une première structure
* une initialisation git
---

### Gérer les dépendances avec `uv`

**Ajouter une dépendance**

Exemple : ajouter `matplotlib`

```bash
uv add matplotlib
```

Cela :

* met à jour le `pyproject.toml`,
* régénère le `uv.lock`.

---

**Supprimer une dépendance**

```bash
uv remove matplotlib
```

---

#### Exécuter du code Python avec `uv`

**Lancer un script Python**

```bash
uv run python script.py
```

Exemple :

```bash
uv run python etl/run_etl.py
```

---

**Utilisation de Jupyter depuis VS Code**

Pour connecter un projet géré par uv à un notebook Jupyter dans VS Code, nous vous recommandons de créer un noyau pour le projet, comme suit :

```bash
uv add --dev ipykernel
```

Lorsque vous êtes invité à sélectionner un noyau, choisissez « Environnements Python » et sélectionnez l’environnement virtuel que vous avez créé précédemment (par exemple, .venv/bin/pythonsous macOS et Linux, 

---

**Lancer une application FastAPI**

```bash
uv run uvicorn api.main:app --reload
```

---

**Lancer Streamlit**

```bash
uv run streamlit run dashboard/app.py
```

---
### Navigation
- [Introduction](https://github.com/Stephane-ISEN/atelierTS/main)
- [Chapitre 2 : modèle pour les séries temproelles ](https://github.com/Stephane-ISEN/atelierLSTM/ch2-ml)


