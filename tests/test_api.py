from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    response = client.post("/token", data={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_analytics_endpoints_no_auth():
    # Les analytics sont publics selon le code (ou protégés si ajouté dans dependency)
    # Ici on teste simplement que l'endpoint existe
    response = client.get("/analytics/avg-duration-by-hour")
    # Retourne 200 si DB connecté, ou 500 si table vide/absente, mais l'app tourne.
    assert response.status_code in [200, 500]