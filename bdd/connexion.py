from __future__ import annotations

import os

import psycopg2
from dotenv import load_dotenv


class ConnexionBDD:
    bdd = None
    curseur = None

    @classmethod
    def connexion(cls):
        load_dotenv()
        if cls.bdd is not None and cls.curseur is not None:
            return cls.bdd, cls.curseur

        cls.bdd = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "atelierts"),
            user=os.getenv("POSTGRES_USER", "atelierts"),
            password=os.getenv("POSTGRES_PASSWORD", "atelierts"),
        )
        cls.curseur = cls.bdd.cursor()
        return cls.bdd, cls.curseur

    @classmethod
    def deconnexion(cls):
        if cls.curseur is not None:
            cls.curseur.close()
            cls.curseur = None

        if cls.bdd is not None:
            cls.bdd.close()
            cls.bdd = None
