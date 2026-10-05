from fastapi.testclient import TestClient

def test_registration_state_machine_flow(client: TestClient):
    phone = "+919876500001"

    # Step 1: Start registration (MEGH)
    res = client.post("/api/registration/start", json={"phone_number": phone})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "LANGUAGE"
    assert "Select language" in data["reply_message"]

    # Step 2: Invalid language response (e.g. "9")
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "9"})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "LANGUAGE"
    assert "Invalid choice" in data["reply_message"]

    # Step 3: Valid language response ("1" for Hindi)
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "1"})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "PIN"
    assert "Enter your 6-digit PIN code" in data["reply_message"]

    # Step 4: Invalid PIN response ("123")
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "123"})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "PIN"
    assert "Invalid PIN code" in data["reply_message"]

    # Step 5: Valid PIN with villages ("441501")
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "441501"})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "VILLAGE"
    assert "Select your village" in data["reply_message"]
    assert "Kalmeshwar" in data["reply_message"]

    # Step 6: Invalid village selection ("99")
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "99"})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "VILLAGE"
    assert "Invalid village option" in data["reply_message"]

    # Step 7: Valid village selection ("1" for Kalmeshwar)
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "1"})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "CROP"
    assert "Select your main crop" in data["reply_message"]
    assert "Soybean" in data["reply_message"]

    # Step 8: Invalid crop selection ("99")
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "99"})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "CROP"
    assert "Invalid crop option" in data["reply_message"]

    # Step 9: Valid crop selection ("1" for Soybean)
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "1"})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "CONSENT"
    assert "Reply YES to continue" in data["reply_message"]

    # Step 10: Invalid consent response ("MAYBE")
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "MAYBE"})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "CONSENT"
    assert "Only YES activates registration" in data["reply_message"]

    # Step 11: Valid consent ("YES") -> Completion!
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "YES"})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "COMPLETED"
    assert data["is_completed"] is True
    assert data["registered_farmer_id"] is not None
    assert "Registration successful" in data["reply_message"]

    # Step 12: Subsequent message from registered farmer
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "HELLO"})
    assert res.status_code == 200
    data = res.json()
    assert "already registered" in data["reply_message"]

    # Step 13: STATUS inquiry
    res = client.post("/api/registration/message", json={"phone_number": phone, "message": "STATUS"})
    assert res.status_code == 200
    data = res.json()
    assert "Meghvani Status: Active" in data["reply_message"]


def test_missed_call_registration_initiation(client: TestClient):
    phone = "+919876599999"
    res = client.post("/api/registration/missed-call", json={"phone_number": phone})
    assert res.status_code == 200
    data = res.json()
    assert data["current_step"] == "LANGUAGE"
    assert "Missed Call Detected" in data["reply_message"]
    assert "Select language" in data["reply_message"]


def test_re_registration_and_reset_flow(client: TestClient):
    phone = "+919876588888"

    # Complete initial registration
    client.post("/api/registration/start", json={"phone_number": phone})
    client.post("/api/registration/message", json={"phone_number": phone, "message": "2"})
    client.post("/api/registration/message", json={"phone_number": phone, "message": "441501"})
    client.post("/api/registration/message", json={"phone_number": phone, "message": "1"})
    client.post("/api/registration/message", json={"phone_number": phone, "message": "1"})
    res_done = client.post("/api/registration/message", json={"phone_number": phone, "message": "YES"})
    assert res_done.json()["is_completed"] is True

    # 1. Verify ALREADY_REGISTERED response
    res_already = client.post("/api/registration/start", json={"phone_number": phone})
    assert res_already.json()["current_step"] == "ALREADY_REGISTERED"
    assert "already registered" in res_already.json()["reply_message"]

    # 2. Re-register via "UPDATE" / "REGISTER AGAIN" message
    res_update = client.post("/api/registration/message", json={"phone_number": phone, "message": "REGISTER AGAIN"})
    assert res_update.status_code == 200
    assert res_update.json()["current_step"] == "LANGUAGE"
    assert "Select language" in res_update.json()["reply_message"]

    # 3. Test force_new on start endpoint
    res_force = client.post("/api/registration/start", json={"phone_number": phone, "force_new": True})
    assert res_force.status_code == 200
    assert res_force.json()["current_step"] == "LANGUAGE"
    assert "Select language" in res_force.json()["reply_message"]

    # 4. Test explicit reset endpoint
    res_reset = client.post("/api/registration/reset", json={"phone_number": phone})
    assert res_reset.status_code == 200
    assert res_reset.json()["current_step"] == "START"

