from fastapi.testclient import TestClient

def test_farmer_creation_success(client: TestClient):
    payload = {
        "phone_number": "+919811122233",
        "preferred_language": "Hindi",
        "pin_code": "441501",
        "village_id": 1,
        "block_id": 1,
        "crop_id": 1,
        "communication_preference": "SMS",
        "consent": True
    }
    response = client.post("/api/farmers", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["phone_number_masked"] == "+91****2233"
    assert data["consent"] is True
    assert data["consent_timestamp"] is not None

def test_farmer_creation_duplicate_rejected(client: TestClient):
    payload = {
        "phone_number": "+919800000001", # Existing seeded phone
        "preferred_language": "Marathi",
        "pin_code": "441501",
        "village_id": 1,
        "block_id": 1,
        "crop_id": 1,
        "communication_preference": "SMS",
        "consent": True
    }
    response = client.post("/api/farmers", json=payload)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]

def test_farmer_creation_no_consent_rejected(client: TestClient):
    payload = {
        "phone_number": "+919833344455",
        "preferred_language": "English",
        "pin_code": "441501",
        "village_id": 1,
        "block_id": 1,
        "crop_id": 1,
        "communication_preference": "SMS",
        "consent": False
    }
    response = client.post("/api/farmers", json=payload)
    assert response.status_code == 422 # Pydantic validator failure

def test_get_farmer_by_id_and_masked_phone(client: TestClient):
    response = client.get("/api/farmers/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["phone_number_masked"] == "+91****0001"
    # Ensure full unmasked phone is not leaked in FarmerRead
    assert "phone_number" not in data

def test_get_farmer_by_phone(client: TestClient):
    response = client.get("/api/farmers/by-phone/+919800000001")
    assert response.status_code == 200
    data = response.json()
    assert data["phone_number_masked"] == "+91****0001"
