from socket import socket
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_socketio import SocketIO ,join_room ,leave_room
from web3 import Web3

import mysql.connector
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
socketio = SocketIO(app)
w3 = Web3(Web3.HTTPProvider("https://eth-mainnet.public.blastapi.io"))

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
    List_Of_Games = Reading_Games_From_DB()
    Jsonify_List_Of_Games = {} 
    for Game in List_Of_Games:
        id, player1, player2, status = Game
        Jsonify_List_Of_Games[id] = {'player1' : player1 , 'player2' : player2 , 'status' : status}
    Response = {'Status Code':200 , 'Games': Jsonify_List_Of_Games}
    return jsonify(Response), 200

@app.route('/Join_To_RockPaperScissors_game',methods=["GET", "POST"])
def Handle_Join_To_RockPaperScissors_game():
    if request.method == 'POST':
        gameId = request.form["gameId"]
        playerhash = request.form["playerhash"]
        paymentHash = request.form["paymentHash"]
        playerName = request.form["playerName"]
        if Check_User_If_Online(playerhash) and Check_Payment_Hash(paymentHash):
            Update_Secound_Player_Address_In_Games_Table(gameId,playerhash,"started")
            Response = {'Event' : 'Join_To_RockPaperScissors' , 'gameId': gameId , 'playerhash' : playerhash , 'playerName' : playerName , 'status' : 'started'}
            return jsonify(Response), 200

@app.route('/Change_User_Online_Status',methods=["GET", "POST"])
def Handle_Change_User_Online_Status():
    if request.method == 'POST': 
        UniqeID = request.form["UniqeID"]
        name = request.form["name"]
        Status = request.form["Status"]
        Update_User_Status_In_Users_Table(UniqeID, Status)

@socketio.on('RockPaperScissorsAdded')
def Handle_RockPaperScissors_Added(game):
    socketio.emit('Rock Paper Scissors Added', game, broadcast=True)

@socketio.on('RockPaperScissorsChanged')
def Handle_RockPaperScissors_Changed(data):
    socketio.emit('Rock Paper Scissors Changed', data, broadcast=True)

def Check_User_If_Online(playerhash):
    List_Of_Users = Reading_Users_From_DB()
    for User in List_Of_Users:
        id, UniqeID, name, Status = User
        if playerhash == UniqeID:
            if Status == "Connected":
                return True
            elif Status == "Disconnected" :
                return False

def Check_Payment_Hash(paymentHash):
    #TODO: work on it for more proof
    try:
        TX = w3.eth.get_transaction(paymentHash)
        return True
    except:
        return False

def Update_User_Status_In_Users_Table(UniqeID,status):
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'UPDATE Users SET status = "{status}" WHERE Uniqeid = {UniqeID};'
    cur.execute(qury)
    db.commit()
    db.close()

def Update_Secound_Player_Address_In_Games_Table(gameId,player,status):
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'UPDATE Games SET player2 = "{player}" WHERE id = {gameId};'
    cur.execute(qury)
    db.commit()
    db.close()
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'UPDATE Games SET status = "{status}" WHERE id = {gameId};'
    cur.execute(qury)
    db.commit()
    db.close()

def writing_Games_to_database(player1,status):
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'INSERT INTO Games VALUES  ("{player1}","0x0000000000000000000000000000000000000000000000000000000000000000","{status}");'
    cur.execute(qury)
    db.commit()
    db.close()

def writing_Users_to_database(UniqeID, name, Status):
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'INSERT INTO Users VALUES  ("{UniqeID}","{name}","{Status}");'
    cur.execute(qury)
    db.commit()
    db.close()

def Reading_Games_From_DB():
    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM Games;")
    db.close()
    return cur.fetchall()

def Reading_Users_From_DB():
    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM Users;")
    db.close()
    return cur.fetchall()

def connect_to_database():
    db = mysql.connector.connect(host=config.MYSQL_HOST,
                       user=config.MYSQL_USER,
                       passwd=config.MYSQL_PASS,
                       db=config.MYSQL_DATABAS)
    return db

if __name__ == '__main__':
    socketio.run(app, debug=True)