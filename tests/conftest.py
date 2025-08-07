import os

import pytest
from backend_app import create_app, socketio

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })

    with app.app_context():
        yield app, socketio

@pytest.fixture
def socketio_client(app):
    app, socketio = app
    client = socketio.test_client(app)
    return client
