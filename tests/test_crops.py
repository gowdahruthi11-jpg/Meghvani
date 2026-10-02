from fastapi.testclient import TestClient

def test_list_crops(client: TestClient):
    response = client.get("/api/crops")
    assert response.status_code == 200
    crops = response.json()
    assert len(crops) >= 3
    crop_names = [c["name"] for c in crops]
    assert "Soybean" in crop_names
    assert "Cotton" in crop_names
    assert "Maize" in crop_names
