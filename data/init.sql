-- init.sql
-- TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- =========================
-- Table: consommation
-- =========================
CREATE TABLE IF NOT EXISTS consommation (
    date_mesure TIMESTAMPTZ NOT NULL,
    consommation_mw DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (date_mesure)
);

-- =========================
-- Table: prediction
-- =========================
CREATE TABLE IF NOT EXISTS prediction (
    date_prediction TIMESTAMPTZ NOT NULL,
    valeur_predite DOUBLE PRECISION,
    PRIMARY KEY (date_prediction)
);

-- =========================
-- Table: mesures
-- =========================
CREATE TABLE IF NOT EXISTS mesures (
    date_mesure TIMESTAMPTZ NOT NULL,

    temperature DOUBLE PRECISION,
    humidite DOUBLE PRECISION,
    vent DOUBLE PRECISION,
    rayonnement DOUBLE PRECISION,

    temperature_prev DOUBLE PRECISION,

    jour INTEGER,
    mois INTEGER,
    weekend BOOLEAN,
    vacances BOOLEAN,
    PRIMARY KEY (date_mesure)
);

-- =========================
-- Hypertables (TimescaleDB)
-- =========================
SELECT create_hypertable('consommation', 'date_mesure', if_not_exists => TRUE);
SELECT create_hypertable('prediction', 'date_prediction', if_not_exists => TRUE);
SELECT create_hypertable('mesures', 'date_mesure', if_not_exists => TRUE);
