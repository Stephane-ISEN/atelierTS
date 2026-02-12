# =========================
# Base image
# =========================
FROM python:3.12-slim

# =========================
# Installation uv
# =========================
RUN pip install --no-cache-dir uv

# =========================
# Dossier de travail
# =========================
WORKDIR /app

# =========================
# Copier fichiers dépendances
# =========================
COPY pyproject.toml uv.lock ./

# Installer dépendances
RUN uv sync --frozen

# =========================
# Copier le code
# =========================
COPY bdd ./bdd
COPY api ./api

RUN mkdir -p /app/mlruns

# =========================
# Exposer le port
# =========================
EXPOSE 8000

# =========================
# Lancer l'API
# =========================
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
