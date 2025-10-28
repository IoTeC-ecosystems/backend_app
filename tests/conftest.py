import os
from datetime import datetime, timedelta
import random
from faker import Faker

import pytest
from backend_app import create_app, socketio
from backend_app.db_mongo import FleetDatabase

# Initialize Faker for generating random data
faker = Faker()

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
    def __init__(self, vehicle_document, var_document):
        self.fleet_vehicle_data = DummyCollection(vehicle_document)
        self.vehicles_variables = DummyCollection(var_document)


class DummyClient:
    def __init__(self, vehicle_document, var_document):
        self.db = DummyDB(vehicle_document, var_document)
    
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
def flask_app():
    app = create_app({
        'TESTING': True,
    })

    with app.app_context():
        yield app, socketio


@pytest.fixture
def socketio_client(flask_app):
    app, socketio = flask_app
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
    vehicle_variables = []
    for vid in ["V1", "V2"]:
        for i in range(10):
            data = {
                "unit-id": vid,
                "engine-speed": round(random.uniform(800, 6000), 2),
                "vehicle-speed": round(random.uniform(0, 200), 2),
                "intake-manifold-absolute-pressure": round(random.uniform(30, 250), 2),
                "relative-throttle-position": round(random.uniform(0, 100), 2),
                "commanded-throttle-actuator": round(random.uniform(0, 100), 2),
                "engine-coolant-temperature": round(random.uniform(80, 110), 2),
                "accelerator-pedal-position": round(random.uniform(0, 100), 2),
                "drivers-demanded-torque": round(random.uniform(0, 100), 2),
                "actual-engine-torque": round(random.uniform(0, 100), 2),
                "timestamp": basetime + timedelta(minutes=i*30)
            }
            vehicle_variables.append(data)
    dummy_client = DummyClient(documents, vehicle_variables)

    def dummy_init(self, connection_str: str = "mongodb://localhost:27017", db_name: str = "fleet_db"):
        self.client = dummy_client
        self.db = self.client[db_name]
        self.vehicles = self.db.fleet_vehicle_data
        self.vehicles_variables = self.db.vehicles_variables
    
    monkeypatch.setattr(FleetDatabase, "__init__", dummy_init)
    yield
