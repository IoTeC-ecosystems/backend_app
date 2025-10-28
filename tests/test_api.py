def test_home(app):
    client = app[0]
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert data["data"] == "connected"


def test_get_vehicles(app):
    client = app[0]
    response = client.get("/api/vehicles")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert set(data["data"]) == {"V1", "V2"}


def test_speed_over_time_empty(app):
    client = app[0]
    response = client.post("/api/speed-over-time", json={"units_id": ["V3"]})
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."


def test_speed_over_time_data(app):
    client = app[0]
    response = client.post('/api/speed-over-time', json={"units_id": ["V1"]})
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data