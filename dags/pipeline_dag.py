# Le DAG Airflow qui lance les scripts Dockerisés.
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'yassine',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'smart_logitrack_pipeline',
    default_args=default_args,
    description='Pipeline ETL Taxi & Training ML',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    # Tache 1 & 2 & 3 : Ingestion + Cleaning + Loading (Script PySpark)
    task_etl = BashOperator(
        task_id='etl_process_silver',
        bash_command='python /opt/project/scripts/etl_silver.py'
    )

    # Tache 4 : Entraînement Modèle
    task_train = BashOperator(
        task_id='train_model',
        bash_command='python /opt/project/scripts/train_model.py'
    )

    task_etl >> task_train