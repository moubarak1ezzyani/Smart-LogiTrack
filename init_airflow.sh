#!/bin/bash
# Initialisation de la DB Airflow
airflow db init
# Création de l'utilisateur Admin
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
#________________________________
# #!/bin/bash
# # init_airflow.sh

# # Initialiser la DB
# airflow db init

# # Créer l'utilisateur Admin
# airflow users create \
#     --username admin \
#     --password admin \
#     --firstname Admin \
#     --lastname User \
#     --role Admin \
#     --email admin@example.com

