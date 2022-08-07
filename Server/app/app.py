from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_socketio import SocketIO ,join_room ,leave_room

import mysql.connector
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
socketio = SocketIO(app)

@app.errorhandler(404)
def page_not_found():
    # note that we set the 404 status explicitly
    return 404

@app.route("/ok")
def sys_check():
    '''this function tell that falsk server is ok and running!!'''
    ret = {'Status code':'200','message':'Server is running...'}
    return jsonify(ret) , 200

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/All_RockPaperScissors_games')
def Handle_All_RockPaperScissors_games():
    List_Of_Games = reading_from_database()
    Jsonify_List_Of_Games = {} 
    for Game in List_Of_Games:
        id, players, status = Game
        Jsonify_List_Of_Games[id] = {'players' : players , 'status' : status}
    Response = {'Status Code':200 , 'Games': Jsonify_List_Of_Games}
    return jsonify(Response), 200

@app.route('/Join_To_RockPaperScissors_game',methods=["GET", "POST"])
def Handle_Join_To_RockPaperScissors_game():
    if request.method == 'POST':
        gameId = request.form["gameId"]
        playerhash = request.form["playerId"]
        paymentHash = request.form["paymentHash"]
        playerName = request.form["playerName"]
        Check_User_If_Connected_To_Socket(playerhashs)

        return 1
        
    return 0 


@socketio.on('RockPaperScissorsAdded')
def Handle_RockPaperScissors_Added(game):
    socketio.emit('Rock Paper Scissors Added', game, broadcast=True)

@socketio.on('RockPaperScissorsChanged')
def Handle_RockPaperScissors_Changed(data):
    socketio.emit('Rock Paper Scissors Changed', data, broadcast=True)

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