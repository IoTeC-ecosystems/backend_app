from backend_app import create_app, socketio

if __name__ == '__main__':
    app = create_app()
    print(vars(socketio))
    socketio.run(app, debug=True)
