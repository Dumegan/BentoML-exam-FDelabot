# Examen BentoML - Prédiction d'admission universitaire

API BentoML qui prédit la chance d'admission d'un étudiant (régression linéaire) à partir de son score GRE, TOEFL, de la note de son université, etc. L'API est sécurisée par un token JWT : il faut se connecter via `/login` avant de pouvoir appeler `/predict`. Le modèle est déjà entraîné et empaqueté dans l'image Docker fournie.

## Commandes pour exécuter le projet

À exécuter dans cet ordre, depuis le dossier où se trouve cette archive.

1. Charger l'image Docker :

```bash
docker load -i admission_prediction_service.tar
```

2. Lancer le service :

```bash
docker run -d --name admission_prediction_service -p 3000:3000 admission_prediction_service:latest
```

Le service est prêt quand `docker logs admission_prediction_service` affiche `Service admission_prediction_service initialized` (quelques secondes).

3. Installer les dépendances de test :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Lancer les tests :

```bash
pytest -v tests/
```

## Endpoints de l'API

- `POST /login` : body `{"username": "admin", "password": "admin123"}` → renvoie `{"access_token": "..."}`.
- `POST /predict` : header `Authorization: Bearer <token>`, body :
  ```json
  {"data": {"gre_score": 330, "toefl_score": 115, "university_rating": 4, "sop": 4.5, "lor": 4.5, "cgpa": 9.2, "research": 1}}
  ```
  → renvoie `{"chance_of_admit": 0.88}`.

Identifiants codés en dur pour la démo (`admin` / `admin123`), à des fins d'évaluation uniquement.

## Contenu de cette archive

Uniquement les 4 éléments requis : `admission_prediction_service.tar`, `requirements.txt`, ce `README.md` et `tests/`. Le code source complet (`src/`, `data/`, `bentofile.yaml`, notebooks d'entraînement...) n'est pas inclus ici.

## Structure du projet complet (dépôt source, pour référence)

```
├── data/
│   ├── raw/            # admission.csv (donnees brutes)
│   └── processed/      # X_train, X_test, y_train, y_test
├── models/
├── src/
│   ├── prepare_data.py # nettoyage + split train/test
│   ├── train_model.py  # entrainement + sauvegarde du modele dans BentoML
│   └── service.py      # API BentoML (login + predict)
├── tests/
│   └── test_service.py
├── bentofile.yaml
├── requirements.txt
└── README.md
```
