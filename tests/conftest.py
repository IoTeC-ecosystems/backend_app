import os

import pytest
from backend_app import create_app, socketio

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })

    yield app

@pytest.fixture
def client(app):
    return socketio.test_client(app)
