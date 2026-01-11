# Notes autour du projet

## DateTime
### strFtime vs strPtime : The Trick 
* `str F time:` Format.

    * **Action:** Date_obj --(format)--> Text
    

    * **Direction:** Object → String.

* `str P time:` Parse.
      
    * **Action:** Text --(parse/understand)--> Date_obj
    * **Direction:** String → Object.

## Instructions de Lancement

* Placez le fichier bronze_taxi.parquet dans le dossier data/.

* Exécutez : `docker-compose up --build`.

* Accédez à Airflow (localhost:8080, admin/admin) et activez le DAG smart_logitrack_pipeline.

* Une fois le DAG terminé (Données Silver créées + Modèle entraîné), testez l'API sur localhost:8000/docs.