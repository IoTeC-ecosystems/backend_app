from datetime import datetime
import numpy as np

from backend_app.vehicle_data import VehicleDataVisualizer
from backend_app.db_mongo import FleetDatabase

from .conftest import DummyClient


def test_get_fields():
    visualizer = VehicleDataVisualizer()
    fields = visualizer.get_fields()
    assert 'engine-speed' in fields
    assert 'vehicle-speed' in fields
    assert 'intake-manifold-absolute-pressure' in fields
    assert 'relative-throttle-position' in fields
    assert 'commanded-throttle-actuator' in fields
    assert 'engine-coolant-temperature' in fields
    assert 'accelerator-pedal-position' in fields
    assert 'drivers-demanded-torque' in fields
    assert 'actual-engine-torque' in fields


def test_compute_distance_traveled():
    visualizer = VehicleDataVisualizer()
    distance = visualizer.compute_distance_traveled()
    assert not distance.empty
    assert 'distance_km' in distance.columns
    assert all(distance['distance_km'] >= 0)
    assert len(distance) > 0
    assert distance[distance['distance_km'] >= 0].shape[0] == distance.shape[0]


def test_compute_distance_traveled_empty(monkeypatch):
    empty_client = DummyClient([], [])

    def empty_init(self, connection_str: str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self.client = empty_client
        self.db = self.client[db_name]
        self.vehicles = self.db.fleet_vehicle_data
        self.vehicles_variables = []

    monkeypatch.setattr(FleetDatabase, "__init__", empty_init)

    visualizer = VehicleDataVisualizer()
    distance = visualizer.compute_distance_traveled()
    assert distance.empty


def test_compute_distance_traveled_single_point(monkeypatch):
    single_point_data = [
        {
            "unit-id": "vehicle_1",
            "timestamp": "2023-10-01T08:00:00Z",
            "latitude": 37.7749,
            "longitude": -122.4194,
        }
    ]
    single_point_client = DummyClient(single_point_data, [])

    def single_point_init(self, connection_str: str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self.client = single_point_client
        self.db = self.client[db_name]
        self.vehicles = self.db.fleet_vehicle_data
        self.vehicles_variables = []

    monkeypatch.setattr(FleetDatabase, "__init__", single_point_init)

    visualizer = VehicleDataVisualizer()
    distance = visualizer.compute_distance_traveled()
    assert len(distance) == 1
    assert distance.iloc[0]['distance_km'] == 0.0


def test_compute_distance_traveled_no_movement(monkeypatch):
    no_movement_data = [
        {
            "unit-id": "vehicle_1",
            "timestamp": "2023-10-01T08:00:00Z",
            "latitude": 37.7749,
            "longitude": -122.4194,
        },
        {
            "unit-id": "vehicle_1",
            "timestamp": "2023-10-01T09:00:00Z",
            "latitude": 37.7749,
            "longitude": -122.4194,
        },
    ]
    no_movement_client = DummyClient(no_movement_data, [])

    def no_movement_init(self, connection_str: str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self.client = no_movement_client
        self.db = self.client[db_name]
        self.vehicles = self.db.fleet_vehicle_data
        self.vehicles_variables = []

    monkeypatch.setattr(FleetDatabase, "__init__", no_movement_init)

    visualizer = VehicleDataVisualizer()
    distance = visualizer.compute_distance_traveled()
    assert len(distance) == 1
    assert distance.iloc[0]['distance_km'] == 0.0

def test_compute_distance_traveled_exception_branch(monkeypatch):
    # Make an entry none to trigger exception branch
    exception_data = [
        {
            "unit-id": "vehicle_1",
            "timestamp": "2023-10-01T08:00:00Z",
            "latitude": 37.7749,
            "longitude": -122.4194,
        },
        {
            "unit-id": "vehicle_1",
            "timestamp": "2023-10-01T09:00:00Z",
            "latitude": None,
            "longitude": -122.4194,
        },
    ]
    exception_client = DummyClient(exception_data, [])
    def exception_init(self, connection_str: str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self.client = exception_client
        self.db = self.client[db_name]
        self.vehicles = self.db.fleet_vehicle_data
        self.vehicles_variables = []
    
    monkeypatch.setattr(FleetDatabase, "__init__", exception_init)

    visualizer = VehicleDataVisualizer()
    distance = visualizer.compute_distance_traveled()
    assert len(distance) == 1
    assert not np.isnan(distance.iloc[0]['distance_km'])
    assert distance.iloc[0]['distance_km'] == 0.0


def test_compute_daily_average():
    visualizer = VehicleDataVisualizer()
    avgs = visualizer.compute_daily_average()

    assert not avgs.empty
    assert 'avg_speed' in avgs.columns
    assert all(avgs['avg_speed'] >= 0)
    assert 'distance_km' in avgs.columns
    assert all(avgs['distance_km'] >= 0)


def test_compute_daily_average_empty(monkeypatch):
    empty_client = DummyClient([], [])

    def empty_init(self, connection_str: str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self.client = empty_client
        self.db = self.client[db_name]
        self.vehicles = self.db.fleet_vehicle_data
        self.vehicles_variables = []

    monkeypatch.setattr(FleetDatabase, "__init__", empty_init)

    visualizer = VehicleDataVisualizer()
    avgs = visualizer.compute_daily_average()
    assert avgs.empty


def test_compute_daily_average_merge_branch(monkeypatch):
    data = [
        {
            "unit-id": "vehicle_1",
            "timestamp": "2023-10-01T08:00:00Z",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "speed": 10,
        },
        {
            "unit-id": "vehicle_1",
            "timestamp": "2023-10-01T08:00:00Z",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "speed": 20,
        },
        {
            "unit-id": "vehicle_1",
            "timestamp": "2023-11-01T08:00:00Z",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "speed": 30,
        },
        {
            "unit-id": "vehicle_1",
            "timestamp": "2023-11-01T08:00:00Z",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "speed": 40,
        },
    ]
    merge_client = DummyClient(data, [])

    def merge_init(self, connection_str: str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self.client = merge_client
        self.db = self.client[db_name]
        self.vehicles = self.db.fleet_vehicle_data
        self.vehicles_variables = []

    monkeypatch.setattr(FleetDatabase, "__init__", merge_init)
    visualizer = VehicleDataVisualizer()
    avgs = visualizer.compute_daily_average()
    assert len(avgs) == 2
    assert set(avgs.columns) == {'unit-id', 'date', 'avg_speed', 'distance_km'}
