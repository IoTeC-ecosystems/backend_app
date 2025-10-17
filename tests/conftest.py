import os
from datetime import datetime, timedelta

import pytest
from backend_app import create_app, socketio
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


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })

    with app.test_client() as client:
        yield client, socketio


@pytest.fixture
def socketio_client(app):
    app, socketio = app
    client = socketio.test_client(app)
    return client


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
