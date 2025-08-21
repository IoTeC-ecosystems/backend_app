import os
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

_CORS = CORS(resources={r"/*": {"origins": "http://localhost:8000/"}}, methods=["GET", "POST"])#resources={r"/*": {"origins": r"^http://localhost:8000.*"}})
socketio = SocketIO(cors_allowed_origins="*")

from . import events

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config.from_pyfile('instance_config.py', silent=True)
        app.secret_key = b'"#$(()(!"()))!"#'
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    socketio.init_app(app, async_mode='threading')

    from .api import main
    app.register_blueprint(main)

    return app
