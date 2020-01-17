from application import app
from flask_socketio import SocketIO, emit

if __name__ == "__main__":
    socketio.run(app)
    #app.run(debug=True)
