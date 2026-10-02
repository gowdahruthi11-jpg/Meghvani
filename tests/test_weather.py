from fastapi.testclient import TestClient

def test_get_block_weather(client: TestClient):
    response = client.get("/api/weather/1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["block_id"] == 1
    assert data[0]["source"] == "DEMO_DATA"

def test_future_forecast_contract(client: TestClient):
    response = client.get("/api/weather/1/forecast")
    assert response.status_code == 200
    data = response.json()
    assert data["block_id"] == 1
    assert data["is_live_prediction"] is False
    assert "NOT CONNECTED YET" in data["disclaimer"]

def test_advisory_rule_evaluation(client: TestClient):
    response = client.post("/api/weather/1/advisory?crop_id=1&language=English")
    assert response.status_code == 200
    data = response.json()
    assert data["crop_name"] == "Soybean"
    assert "advisory" in data
    assert data["advisory"]["decision"] in ["SOW_NOW", "WAIT", "PROTECT_CROP", "DRAIN_FIELD", "CHECK_LOCAL_ADVICE"]
    assert "Soybean" in data["advisory"]["message"]
