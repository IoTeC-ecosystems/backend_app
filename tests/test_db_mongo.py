from datetime import datetime, timedelta
import pandas as pd
import pytest

from backend_app.db_mongo import FleetDatabase

from .conftest import DummyClient


def test_db_connection():
    db_instance = FleetDatabase()
    assert db_instance.client is not None
    assert db_instance.db is not None
    assert db_instance.vehicles is not None


def test_empty_db(monkeypatch):
    empty_client = DummyClient([])

    def empty_init(self, connection_str: str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self.client = empty_client
        self.db = self.client[db_name]
        self.vehicles = self.db.fleet_vehicle_data

    monkeypatch.setattr(FleetDatabase, "__init__", empty_init)
    db_instance = FleetDatabase()
    vehicles = db_instance.get_all_vehicles()
    assert vehicles == []
    vehicles_data = db_instance.get_vehicle_data(["V1"])
    assert vehicles_data.empty
    vehicles_range = db_instance.get_range_data(["V1"], "2023-01-01", "2023-01-02")
    assert vehicles_range.empty


def test_get_all_vehicles():
    db_instance = FleetDatabase()
    vehicles = db_instance.get_all_vehicles()
    assert set(vehicles) == {"V1", "V2"}


def test_get_vehicle_data_no_time():
    db_instance = FleetDatabase()
    vehicles_data = db_instance.get_vehicle_data(["V1"])
    assert not vehicles_data.empty
    assert set(vehicles_data['unit-id'].unique()) == {"V1"}


def test_get_vehicle_data_start_only():
    db_instance = FleetDatabase()
    start_only = datetime(2023, 1, 1, 0, 10) # ten minutes afte basetime (line 55)
    vehicles = db_instance.get_vehicle_data(["V1"], start_time=start_only)
    assert not vehicles.empty
    assert vehicles['timestamp'].min() >= start_only


def test_get_vehicle_data_end_only():
    db_instance = FleetDatabase()
    end_only = datetime(2023, 1, 1, 0, 15) # 15 min after basetime (line 55)
    vehicles = db_instance.get_vehicle_data(["V1"], end_time=end_only)
    assert not vehicles.empty
    assert vehicles['timestamp'].max() <= end_only


def test_get_range_data():
    db_instance = FleetDatabase()
    start_date = "2023-01-01"
    end_date = "2023-01-02"
    vehicles = db_instance.get_range_data(["V1", "V2"], start_date, end_date)
    assert not vehicles.empty
    assert set(vehicles['unit-id'].unique()) == {"V1", "V2"}
    assert vehicles['timestamp'].min() >= datetime.fromisoformat(start_date)
    assert vehicles['timestamp'].max() <= datetime.fromisoformat(end_date) + timedelta(days=1) - timedelta(seconds=1)
