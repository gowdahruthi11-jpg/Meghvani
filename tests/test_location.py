from fastapi.testclient import TestClient

def test_list_blocks(client: TestClient):
    response = client.get("/api/blocks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert data[0]["name"] == "Nagpur Rural"

def test_get_block_by_id(client: TestClient):
    response = client.get("/api/blocks/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Nagpur Rural"
    assert data["district"] == "Nagpur"

def test_get_block_not_found(client: TestClient):
    response = client.get("/api/blocks/9999")
    assert response.status_code == 404

def test_get_villages_by_pin(client: TestClient):
    response = client.get("/api/villages/by-pin/441501")
    assert response.status_code == 200
    villages = response.json()
    assert len(villages) == 2
    names = [v["name"] for v in villages]
    assert "Kalmeshwar" in names
    assert "Mohpa" in names

def test_get_villages_invalid_pin(client: TestClient):
    response = client.get("/api/villages/by-pin/123")
    assert response.status_code == 400
    assert "exactly 6 numeric digits" in response.json()["detail"]
