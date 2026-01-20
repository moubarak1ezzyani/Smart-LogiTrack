from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, unix_timestamp
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor, RandomForestRegressionModel
import os

# CONFIG
data_path=os.getenv("DATA_PATH_env")
MODEL_PATH = os.getenv("DATA_PATH_env")
DB_URL = os.getenv("DATA_PATH_env")
DB_PROPS = os.getenv("DATA_PATH_env")

def get_spark():
    return SparkSession.builder \
        .appName("SmartLogiTrack") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0") \
        .getOrCreate()

# Tache 1 & 2 : Ingestion (Simulé ici par création de dummy data si absent)
def ingest_data():
    spark = get_spark()
    # En situation réelle : wget ou request sur l'URL du dataset
    # Ici, on crée un dataset bidon si le fichier n'existe pas pour l'exemple
    if not os.path.exists(data_path):
        data = [
            (1, "2024-01-01 10:00:00", "2024-01-01 10:20:00", 2.5, 1, 15.0),
            (2, "2024-01-01 11:00:00", "2024-01-01 11:45:00", 10.0, 2, 40.0),
             (2, "2024-01-01 11:00:00", "2024-01-01 11:45:00", -5.0, 2, 40.0) # Outlier
        ]
        cols = ["VendorID", "tpep_pickup_datetime", "tpep_dropoff_datetime", "trip_distance", "payment_type", "total_amount"]
        df = spark.createDataFrame(data, cols)
        df.write.mode("overwrite").parquet(data_path)
    print("Données Bronze disponibles.")

# Tache 3 : Nettoyage & Silver (PostgreSQL)
def process_silver():
    spark = get_spark()
    df = spark.read.parquet(data_path)
    
    # Feature Engineering (Notebook logic)
    df = df.withColumn("duration_minutes", 
             (unix_timestamp(col("tpep_dropoff_datetime")) - unix_timestamp(col("tpep_pickup_datetime"))) / 60)
    
    # Nettoyage (Filtres du brief)
    df_clean = df.filter(
        (col("trip_distance") > 0) & (col("trip_distance") < 200) &
        (col("duration_minutes") > 0)
    )
    
    # Sauvegarde PostgreSQL (Silver)
    df_clean.write.jdbc(url=DB_URL, table="silver_taxi_trips", mode="overwrite", properties=DB_PROPS)
    print("Données Silver sauvegardées dans PostgreSQL.")

# Tache 4 : Entrainement ML
def train_model():
    spark = get_spark()
    # Lire depuis PostgreSQL
    df = spark.read.jdbc(url=DB_URL, table="silver_taxi_trips", properties=DB_PROPS)
    
    # Vector Assembler
    assembler = VectorAssembler(inputCols=["trip_distance", "payment_type"], outputCol="features")
    df_ready = assembler.transform(df).select("features", "duration_minutes")
    
    # Train (Random Forest comme discuté)
    rf = RandomForestRegressor(featuresCol="features", labelCol="duration_minutes", numTrees=10)
    model = rf.fit(df_ready)
    
    # Serialisation (Sauvegarde)
    model.write().overwrite().save(MODEL_PATH)
    print(f"Modèle sauvegardé dans {MODEL_PATH}")

# DAG Definition
default_args = {'owner': 'airflow', 'start_date': datetime(2024, 1, 1)}

with DAG('smart_logitrack_etl', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:
    t1 = PythonOperator(task_id='ingest', python_callable=ingest_data)
    t2 = PythonOperator(task_id='silver_process', python_callable=process_silver)
    t3 = PythonOperator(task_id='train_ml', python_callable=train_model)

    t1 >> t2 >> t3