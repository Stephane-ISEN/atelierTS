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
