# Série temporelle consommation d'énergie

Projet de prévision de consommation électrique (Brest Métropole) avec une base **PostegreSQL**.

---

## Introduction à PostgreSQL

PostgreSQL est un système de gestion de base de données relationnelle open-source reconnu pour sa robustesse, sa conformité aux standards SQL et sa capacité à gérer des volumes de données importants. Contrairement à des bases plus légères ou orientées documents, PostgreSQL repose sur un modèle relationnel strict : les données sont organisées en tables, composées de colonnes typées et de lignes représentant des enregistrements. Chaque table peut être contrainte par des règles d’intégrité comme des clés primaires, des contraintes d’unicité ou des relations entre tables.

Dans un projet de prévision énergétique comme le tien, PostgreSQL permet de structurer clairement les différentes natures de données : les consommations observées, les prédictions générées par le modèle, et les variables explicatives utilisées pour entraîner ce modèle. Cette séparation logique favorise la lisibilité, la maintenance et l’évolutivité du système.

---

## Pourquoi ajouter TimescaleDB ?

Lorsque les données sont organisées autour du temps — comme des consommations journalières ou des mesures météorologiques — on parle de séries temporelles. Les bases relationnelles classiques peuvent les stocker, mais elles ne sont pas optimisées pour des requêtes massives par plage de dates ou pour des insertions continues à haute fréquence.

TimescaleDB est une extension de PostgreSQL conçue précisément pour ce type d’usage. Elle introduit le concept d’“hypertable”, qui permet de partitionner automatiquement les données temporelles en segments internes appelés chunks. Cette partition est transparente pour l’utilisateur : on continue à interroger la table comme une table classique, mais les performances sont bien meilleures sur des volumes importants.

Dans ton architecture, transformer les tables `consommation`, `prediction` et `mesures` en hypertables permet d’assurer une gestion efficace des données dans la durée, tout en conservant la simplicité du SQL standard.

---

## Rôle du fichier init.sql

Le fichier `init.sql` est exécuté automatiquement lors de l’initialisation du conteneur PostgreSQL (par exemple dans un environnement Docker). Il sert à définir l’état initial de la base de données : activation des extensions, création des tables, définition des contraintes et transformation en hypertables.

Ce fichier joue un rôle central dans la reproductibilité de ton environnement. Il garantit que toute nouvelle instance de la base possède la même structure, sans intervention manuelle. Ajouter une nouvelle table comme `mesures` dans ce fichier revient donc à intégrer définitivement cette structure dans l’architecture de la base.

```bash
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS consommation (
    id BIGSERIAL PRIMARY KEY,
    date_mesure TIMESTAMPTZ NOT NULL,
    consommation_mw DOUBLE PRECISION NOT NULL,
    UNIQUE (date_mesure)
);

CREATE TABLE IF NOT EXISTS prediction (
    id BIGSERIAL PRIMARY KEY,
    date_prediction TIMESTAMPTZ NOT NULL,
    valeur_predite DOUBLE PRECISION,
    UNIQUE (date_prediction)
);

SELECT create_hypertable('consommation', 'date_mesure', if_not_exists => TRUE);
SELECT create_hypertable('prediction', 'date_prediction', if_not_exists => TRUE);
```

---

## Ajouter la table mesures : logique conceptuelle

La table `mesures` doit représenter les variables utilisées pour les prédictions du modèle LSTM multivarié. Elle regroupe les observations météorologiques, certaines valeurs prévisionnelles ainsi que des variables calendaires.

dans le init.sql ajouter une nouvelle table qui contient : 
- un id,
- un timestamp,
- temperature,
- humidite,
- vent,
- rayonnement,
- temperature_prev,
- jour,
- mois,
- weekend,
- vacances.

C'est aussi une hypertable.

Une fois la table créée de manière classique, elle doit être convertie en hypertable en indiquant que la colonne temporelle constitue l’axe de partition. Cette transformation permet à TimescaleDB de gérer automatiquement la segmentation interne des données.

---

Voici une explication claire et rédigée pour ton tutoriel, suivie du code et d’une méthode simple de vérification.

---

## docker-compose

Ajoute les lignes suivantes dans le docker-compose, afin de créer la base PostegreSQL.

```yaml
version: "3.9"

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg17
    container_name: atelierts-timescaledb
    restart: unless-stopped
    env_file:
      - .env
    ports:
      - "5432:5432"
    volumes:
      - ./data/init.sql:/docker-entrypoint-initdb.d/init.sql
      - ./data/postgresql:/var/lib/postgresql/data
```

---

### Vérifier que le conteneur fonctionne

```bash
docker compose ps
```

Le service doit être en état `Up`.

---

### Vérifier les logs

```bash
docker compose logs timescaledb
```

Lors du premier lancement, tu dois voir :

* La création de la base
* L’exécution du script `init.sql`
* L’activation de TimescaleDB

---

### Se connecter à la base

Depuis le terminal :

```bash
docker exec -it atelierts-timescaledb psql -U postgres
```

Puis vérifier les tables :

```sql
\dt
```

Tu dois voir :

* consommation
* prediction
* mesures

---

### Vérifier que ce sont bien des hypertables

Toujours dans psql :

```sql
SELECT hypertable_name FROM timescaledb_information.hypertables;
```

Les trois tables doivent apparaître.

---

