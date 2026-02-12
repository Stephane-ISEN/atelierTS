# Série temporelle consommation d'énergie

Projet de prévision de consommation électrique (Brest Métropole).
Intégration  de la base **PostegreSQL** à **FastAPI**.

---

## Ajout d'un service de lecture de bdd

Dans le répertoire `./api`, il faut compléter la fonction `get_features_for_day()` du script `services.py`.

Ce code doit : 
* Interroge PostgreSQL pour récupérer les 30 jours précédents
* Reconstruit dynamiquement les features nécessaires
* Génère les décalages temporels en mémoire
* Construit la séquence LSTM
* Retourne un tenseur prêt pour `model.predict()`



---

## Ajout d'un service d'écriture en bdd
