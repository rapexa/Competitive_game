from flask import Flask, render_template
from flask_socketio import SocketIO
import mysql.connector
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
socketio = SocketIO(app)

@socketio.on('RockPaperScissorsAdded')
def handle_RockPaperScissors_Added(data):
    socketio.emit('my response', data, broadcast=True)

@socketio.on('RockPaperScissorsChanged')
def handle_RockPaperScissors_Changed(data):
    socketio.emit('my response', data, broadcast=True)

def writing_to_database(name,titlew,message):
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'INSERT INTO works VALUES ("{name}","{titlew}","{message}");'
    cur.execute(qury)
    db.commit()
    db.close()

def reading_from_database():
    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM works;")
    db.close()
    return cur.fetchall()

def connect_to_database():
    db = mysql.connector.connect(host=config.MYSQL_HOST,
                       user=config.MYSQL_USER,
                       passwd=config.MYSQL_PASS,
                       db=config.MYSQL_DB,
                       charset=config.charset)
    return db

if __name__ == '__main__':
    socketio.run(app)