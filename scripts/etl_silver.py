# Nettoyage PySpark et chargement dans PostgreSQL (Zone Silver).
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, unix_timestamp, hour, dayofweek, month

# Config DB
DB_URL = "jdbc:postgresql://postgres:5432/logitrack"
DB_PROPS = {"user": "user", "password": "password", "driver": "org.postgresql.Driver"}

def run_etl():
    # 1. Init Spark avec driver JDBC Postgres (téléchargé auto ou présent dans l'env)
    spark = SparkSession.builder \
        .appName("SmartLogiTrack_ETL") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.2.18") \
        .getOrCreate()

    # 2. Ingestion Bronze (Parquet)
    df = spark.read.parquet("/opt/project/data/bronze_taxi.parquet")

    # 3. Nettoyage & Feature Engineering (Silver)
    # Calcul durée en minutes
    df = df.withColumn("duration_minutes", 
        (unix_timestamp("tpep_dropoff_datetime") - unix_timestamp("tpep_pickup_datetime")) / 60
    )

    # Filtrage (Règles métier)
    df_silver = df.filter(
        (col("trip_distance") > 0) & (col("trip_distance") <= 200) &
        (col("duration_minutes") > 0) &
        (col("passenger_count") > 0)
    )

    # Ajout features temporelles
    df_silver = df_silver.withColumn("pickup_hour", hour("tpep_pickup_datetime")) \
                         .withColumn("day_of_week", dayofweek("tpep_pickup_datetime")) \
                         .withColumn("month", month("tpep_pickup_datetime"))

    # 4. Stockage PostgreSQL (Table silver_taxi_trips)
    mode = "overwrite"
    df_silver.select(
        "tpep_pickup_datetime", "passenger_count", "trip_distance", 
        "PULocationID", "DOLocationID", "payment_type", "total_amount", 
        "duration_minutes", "pickup_hour", "day_of_week", "month"
    ).write.jdbc(DB_URL, "silver_taxi_trips", mode=mode, properties=DB_PROPS)

    print("ETL Terminé : Données chargées dans PostgreSQL.")
    spark.stop()

if __name__ == "__main__":
    run_etl()