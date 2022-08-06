from flask import Flask, render_template
from flask_socketio import SocketIO
import mysql.connector
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
socketio = SocketIO(app)

if __name__ == '__main__':
    socketio.run(app)