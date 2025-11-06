from .conftest import DummyClient, FleetDatabase

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


def test_speed_over_time_only_start(app):
    client = app[0]
    response = client.post('/api/speed-over-time', json={
        "units_id": ["V1"],
        "start_time": "2023-01-01T00:30:00"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data


def test_speed_over_time_only_end(app):
    client = app[0]
    response = client.post('/api/speed-over-time', json={
        "units_id": ["V1"],
        "end_time": "2023-01-01T00:30:00"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data


def test_speed_over_time_start_end(app):
    client = app[0]
    response = client.post('/api/speed-over-time', json={
        "units_id": ["V1"],
        "start_time": "2023-01-01T00:15:00",
        "end_time": "2023-01-01T00:45:00"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data


def test_speed_over_time_no_data_in_range(app):
    client = app[0]
    response = client.post('/api/speed-over-time', json={
        "units_id": ["V1"],
        "start_time": "2022-12-31T23:00:00",
        "end_time": "2022-12-31T23:30:00"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 400
    assert data["data"] == "No data available for the selected parameters."


def test_speed_over_time_multiple_vehicles(app):
    client = app[0]
    response = client.post('/api/speed-over-time', json={
        "units_id": ["V1", "V2"]
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data


def test_speed_over_time_no_vehicles(app):
    client = app[0]
    response = client.post('/api/speed-over-time', json={
        "units_id": []
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 400
    assert data["data"] == "No data available for the selected parameters."


def test_daily_distance_empty(app):
    client = app[0]
    response = client.post("/api/daily-distance", json={"units_id": ["V3"]})
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."


def test_daily_distance_data(app):
    client = app[0]
    response = client.post('/api/daily-distance', json={"units_id": ["V1"]})
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data

def test_daily_distance_only_start(app):
    client = app[0]
    response = client.post('/api/daily-distance', json={
        "units_id": ["V1"],
        "start_time": "2023-01-01T00:30:00"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data


def test_daily_distance_only_end(app):
    client = app[0]
    response = client.post('/api/daily-distance', json={
        "units_id": ["V1"],
        "end_time": "2023-01-01T00:30:00"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data


def test_daily_distance_start_end(app):
    client = app[0]
    response = client.post('/api/daily-distance', json={
        "units_id": ["V1"],
        "start_time": "2023-01-01T00:15:00",
        "end_time": "2023-01-01T00:45:00"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data

def test_daily_distance_no_data_in_range(app):
    client = app[0]
    response = client.post('/api/daily-distance', json={
        "units_id": ["V1"],
        "start_time": "2022-12-31T23:00:00",
        "end_time": "2022-12-31T23:30:00"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 400
    assert data["data"] == "No data available for the selected parameters."


def test_daily_distance_multiple_vehicles(app):
    client = app[0]
    response = client.post('/api/daily-distance', json={
        "units_id": ["V1", "V2"]
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data


def test_average_speed_distance_empty(app):
    client = app[0]
    response = client.post("/api/average-speed-distance", json={"unit_id": "V3"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."


def test_average_speed_distance_data(app):
    client = app[0]
    response = client.post('/api/average-speed-distance', json={"unit_id": "V1"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_average_speed_distance_with_time_start(app):
    client = app[0]
    response = client.post('/api/average-speed-distance', json={
        "unit_id": "V1",
        "start_time": "2023-01-01T00:15:00",
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_average_speed_distance_with_time_end(app):
    client = app[0]
    response = client.post('/api/average-speed-distance', json={
        "unit_id": "V1",
        "end_time": "2023-01-01T00:45:00",
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_timeseries_empty(app):
    client = app[0]
    response = client.post("/api/plot/timeseries", json={
        "units_id": ["V3"],
        "field": "engine-speed"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."

    response = client.post("/api/plot/timeseries", json={
        "units_id": [],
        "field": "engine-speed"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."

    response = client.post("/api/plot/timeseries", json={
        "units_id": ["V1"],
        "start_time": "2022-12-31T23:00:00",
        "end_time": "2022-12-31T23:30:00",
        "field": "engine-speed"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."


def test_plot_timeseries_no_field(app):
    client = app[0]
    response = client.post("/api/plot/timeseries", json={
        "units_id": ["V1"]
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "Field parameter is required."


def test_plot_timeseries_data(app):
    client = app[0]
    response = client.post('/api/plot/timeseries', json={
        "units_id": ["V1"],
        "field": "engine-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_timeseries_multiple_vehicles(app):
    client = app[0]
    response = client.post('/api/plot/timeseries', json={
        "units_id": ["V1", "V2"],
        "field": "engine-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_timeseries_with_time_range(app):
    client = app[0]
    response = client.post('/api/plot/timeseries', json={
        "units_id": ["V1"],
        "start_time": "2023-01-01T00:15:00",
        "end_time": "2023-01-01T00:45:00",
        "field": "engine-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_distribution_empty(app):
    client = app[0]
    response = client.post("/api/plot/distribution", json={
        "units_id": ["V3"],
        "field": "engine-speed"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."

    response = client.post("/api/plot/distribution", json={
        "units_id": [],
        "field": "engine-speed"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."

    response = client.post("/api/plot/distribution", json={
        "units_id": ["V1"],
        "start_time": "2022-12-31T23:00:00",
        "end_time": "2022-12-31T23:30:00",
        "field": "engine-speed"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."


def test_plot_distribution_no_field(app):
    client = app[0]
    response = client.post("/api/plot/distribution", json={
        "units_id": ["V1"]
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "Field parameter is required."


def test_plot_distribution_data(app):
    client = app[0]
    response = client.post('/api/plot/distribution', json={
        "units_id": ["V1"],
        "field": "engine-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_distribution_multiple_vehicles(app):
    client = app[0]
    response = client.post('/api/plot/distribution', json={
        "units_id": ["V1", "V2"],
        "field": "engine-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_distribution_with_time_range(app):
    client = app[0]
    response = client.post('/api/plot/distribution', json={
        "units_id": ["V1"],
        "start_time": "2023-01-01T00:15:00",
        "end_time": "2023-01-01T00:45:00",
        "field": "engine-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)    


def test_plot_boxplot_empty(app):
    client = app[0]
    response = client.post("/api/plot/boxplot", json={
        "units_id": ["V3"],
        "field": "engine-speed"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."

    response = client.post("/api/plot/boxplot", json={
        "units_id": [],
        "field": "engine-speed"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."

    response = client.post("/api/plot/boxplot", json={
        "units_id": ["V1"],
        "start_time": "2022-12-31T23:00:00",
        "end_time": "2022-12-31T23:30:00",
        "field": "engine-speed"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."


def test_plot_boxplot_no_field(app):
    client = app[0]
    response = client.post("/api/plot/boxplot", json={
        "units_id": ["V1"]
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "Field parameter is required."


def test_plot_boxplot_data(app):
    client = app[0]
    response = client.post('/api/plot/boxplot', json={
        "units_id": ["V1"],
        "field": "engine-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_boxplot_multiple_vehicles(app):
    client = app[0]
    response = client.post('/api/plot/boxplot', json={
        "units_id": ["V1", "V2"],
        "field": "engine-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_boxplot_with_time_range(app):
    client = app[0]
    response = client.post('/api/plot/boxplot', json={
        "units_id": ["V1"],
        "start_time": "2023-01-01T00:15:00",
        "end_time": "2023-01-01T00:45:00",
        "field": "engine-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_scatter_empty(app):
    client = app[0]
    response = client.post("/api/plot/scatter", json={
        "units_id": ["V3"],
        "field_x": "engine-speed",
        "field_y": "vehicle-speed"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."

    response = client.post("/api/plot/scatter", json={
        "units_id": [],
        "field_x": "engine-speed",
        "field_y": "vehicle-speed"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters." 

    response = client.post("/api/plot/scatter", json={
        "units_id": ["V1"],
        "start_time": "2022-12-31T23:00:00",
        "end_time": "2022-12-31T23:30:00",
        "field_x": "engine-speed",
        "field_y": "vehicle-speed"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."


def test_plot_scatter_no_fields(app):
    client = app[0]
    response = client.post("/api/plot/scatter", json={
        "units_id": ["V1"]
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "Both field_x and field_y parameters are required."


def test_plot_scatter_data(app):
    client = app[0]
    response = client.post('/api/plot/scatter', json={
        "units_id": ["V1"],
        "field_x": "engine-speed",
        "field_y": "vehicle-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_scatter_multiple_vehicles(app):
    client = app[0]
    response = client.post('/api/plot/scatter', json={
        "units_id": ["V1", "V2"],
        "field_x": "engine-speed",
        "field_y": "vehicle-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_scatter_with_time_range(app):
    client = app[0]
    response = client.post('/api/plot/scatter', json={
        "units_id": ["V1"],
        "start_time": "2023-01-01T00:15:00",
        "end_time": "2023-01-01T00:45:00",
        "field_x": "engine-speed",
        "field_y": "vehicle-speed"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_heatmap_data(app):
    client = app[0]
    response = client.post('/api/plot/heatmap', json={
        "unit_id": "V1",
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)


def test_plot_heatmap_no_vehicle(app):
    client = app[0]
    response = client.post('/api/plot/heatmap', json={
        "unit_id": "V3",
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."

    response = client.post('/api/plot/heatmap', json={
        "unit_id": "",
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "unit_id parameter is required."

    response = client.post("/api/plot/heatmap", json={
        "unit_id": "V1",
        "start_time": "2022-12-31T23:00:00",
        "end_time": "2022-12-31T23:30:00"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == 400
    assert "data" in data
    assert data["data"] == "No data available for the selected parameters."    


def test_plot_heatmap_with_time_range(app):
    client = app[0]
    response = client.post('/api/plot/heatmap', json={
        "unit_id": "V1",
        "start_time": "2023-01-01T00:15:00",
        "end_time": "2023-01-01T00:45:00"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == 200
    assert "data" in data
    assert isinstance(data["data"], str)
