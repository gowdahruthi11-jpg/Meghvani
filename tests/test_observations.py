from datetime import date
from fastapi.testclient import TestClient

def test_submit_farmer_observation(client: TestClient):
    payload = {
        "farmer_id": 1,
        "block_id": 1,
        "observation_date": str(date.today()),
        "observation_type": "RAIN",
        "value": 25.0,
        "source": "FARMER"
    }
    response = client.post("/api/observations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["observation_type"] == "RAIN"
    assert data["value"] == 25.0
    assert data["farmer_id"] == 1

def test_submit_observation_invalid_farmer(client: TestClient):
    payload = {
        "farmer_id": 99999,
        "block_id": 1,
        "observation_date": str(date.today()),
        "observation_type": "DRY"
    }
    response = client.post("/api/observations", json=payload)
    assert response.status_code == 404

def test_get_observations_by_block(client: TestClient):
    response = client.get("/api/observations/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
