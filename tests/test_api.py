def test_get_vehicles(app):
    client = app[0]
    response = client.get("/api/vehicles")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert set(data["data"]) == {"V1", "V2"}


