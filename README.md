# Smart-LogiTrack
Système Prédictif de Transport Urbain (ETA)

### Arborescence
```bash
SMART-LOGITRACK/
├── dags/
│   └── pipeline_dag.py         # Orchestration Airflow
├── scripts/                    # Scripts exécutés par Airflow
│   ├── etl_silver.py           # PySpark: Nettoyage & Ingestion DB
│   └── train_model.py          # Entraînement ML & Sérialisation
├── app/                        # Application API
│   ├── main.py                 # Endpoints FastAPI (Predict & Analytics)
│   └── auth.py                 # Gestion JWT & Sécurité
├── data/
│   └── bronze_taxi.parquet     # Fichier source fourni
├── models/                     # Stockage du modèle
│   └── model.pkl
├── tests/
│   └── test_app.py             # Tests unitaires Pytest
├── docker-compose.yml          # Orchestration des conteneurs
├── Dockerfile                  # Image custom (Python + Java pour Spark)
├── requirements.txt            # Dépendances Python
└── init_airflow.sh             # Script d'initialisation
```