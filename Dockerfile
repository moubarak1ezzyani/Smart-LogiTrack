FROM apache/airflow:2.7.1
USER root
# --- java
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk-headless && \
    apt-get clean
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#================================================================
# FROM python:3.9-slim

# # Installation de Java (Requis pour PySpark) et outils système
# RUN apt-get update && \
#     apt-get install -y openjdk-17-jre-headless gcc libpq-dev && \
#     apt-get clean

# # Variables d'environnement pour Spark et Python
# ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# WORKDIR /opt/project

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copie du code source
# COPY . .