CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS consommation (
    id BIGSERIAL PRIMARY KEY,
    date_mesure TIMESTAMPTZ NOT NULL,
    consommation_mw DOUBLE PRECISION NOT NULL,
    source TEXT NOT NULL DEFAULT 'odre.opendatasoft.com',
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (date_mesure)
);

CREATE TABLE IF NOT EXISTS prediction (
    id BIGSERIAL PRIMARY KEY,
    date_prediction TIMESTAMPTZ NOT NULL,
    valeur_reelle DOUBLE PRECISION,
    valeur_predite DOUBLE PRECISION,
    modele TEXT NOT NULL DEFAULT 'baseline_j-1',
    cree_le TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (date_prediction, modele)
);

SELECT create_hypertable('consommation', 'date_mesure', if_not_exists => TRUE);
SELECT create_hypertable('prediction', 'date_prediction', if_not_exists => TRUE);
