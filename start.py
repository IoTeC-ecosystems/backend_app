from backend_app import create_app, socketio, _CORS

if __name__ == '__main__':
    app = create_app()
    _CORS.init_app(app)
    socketio.run(app, debug=True)
