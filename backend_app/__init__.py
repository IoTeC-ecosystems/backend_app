import os
from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile('instance_config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    socketio.init_app(app, async_mode='threading')

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app)
