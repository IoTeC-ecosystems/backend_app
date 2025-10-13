from datetime import datetime, timedelta
import pandas as pd
import pytest

from backend_app.db_mongo import FleetDatabase


class DummyCollection:
    def __init__(self, documents):
        self._docs = documents

    def distinct(self, field):
        return sorted(list({d[field] for d in self._docs if field in d}))

    def find(self, query):
        unit_ids = query.get("unit-id", {}).get("$in", [])
        ts_filter = query.get("timestamp", {})
        results = []
        for d in self._docs:
            if d["unit-id"] not in unit_ids:
                continue
            if ts_filter:
                gte = ts_filter.get("$gte")
                lte = ts_filter.get("$lte")
                if gte and d["timestamp"] < gte:
                    continue
                if lte and d["timestamp"] > lte:
                    continue
            results.append(d)
        class Cursor(list):
            def sort(self, field, direction):
                reverse = direction == -1
                return Cursor(sorted(self, key=lambda x: x[field], reverse=reverse))
        return Cursor(results)


class DummyDB:
    def __init__(self, documents):
        self.fleet_vehicle_data = DummyCollection(documents)


class DummyClient:
    def __init__(self, documents):
        self.db = DummyDB(documents)
    
    def __getitem__(self, name):
        return self.db
    
    def close(self):
        pass


@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    basetime = datetime(2023, 1, 1, 0, 0)
    documents = []
    for vid in ["V1", "V2"]:
        for i in range(10):
            documents.append({
                "unit-id": vid,
                'latitude': 10.0 + i*0.02 + (0.05 if vid == "V2" else 0),
                'longitude': 20.0 + i*0.02,
                'speed': 50 + i*5,
                'timestamp': basetime + timedelta(minutes=i*30)
            })
    dummy_client = DummyClient(documents)

    def dummy_init(self, connection_str: str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self.client = dummy_client
        self.db = self.client[db_name]
        self.vehicles = self.db.fleet_vehicle_data
    
    monkeypatch.setattr(FleetDatabase, "__init__", dummy_init)
    yield


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
