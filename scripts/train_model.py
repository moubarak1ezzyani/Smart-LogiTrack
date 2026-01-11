import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Connexion DB
DB_URI = "postgresql://user:password@postgres:5432/logitrack"

def train():
    engine = create_engine(DB_URI)
    
    # 1. Chargement des données Silver depuis Postgres
    query = "SELECT trip_distance, passenger_count, pickup_hour, day_of_week, duration_minutes FROM silver_taxi_trips LIMIT 50000"
    df = pd.read_sql(query, engine)
    
    # 2. Préparation
    X = df[['trip_distance', 'passenger_count', 'pickup_hour', 'day_of_week']]
    y = df['duration_minutes']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 3. Entraînement (Random Forest)
    model = RandomForestRegressor(n_estimators=10, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # 4. Évaluation
    preds = model.predict(X_test)
    print(f"MAE: {mean_absolute_error(y_test, preds)}")
    print(f"R2 Score: {r2_score(y_test, preds)}")
    
    # 5. Sérialisation
    joblib.dump(model, '/opt/project/models/model.pkl')
    print("Modèle sauvegardé dans models/model.pkl")

if __name__ == "__main__":
    train()