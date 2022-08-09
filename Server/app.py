from ast import Return
from pickle import TRUE
from socket import socket
from typing import Type
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_socketio import SocketIO ,join_room ,leave_room
from web3 import Web3

import pymysql
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
socketio = SocketIO(app)
w3 = Web3(Web3.HTTPProvider("https://eth-mainnet.public.blastapi.io"))

@app.route("/ok")
def sys_check():
    ''''''
    ret = {'Status code':'200','message':'Server is running...'}
    return jsonify(ret) , 200

@app.route('/All_RockPaperScissors_games')
def Handle_All_RockPaperScissors_games():
    ''''''
    List_Of_Games = Reading_Games_From_DB()
    Jsonify_List_Of_Games = {} 
    for Game in List_Of_Games:
        id, player1, player2, status = Game
        Jsonify_List_Of_Games[id] = {'player1' : player1 , 'player2' : player2 , 'status' : status}
    Response = {'Status Code':200 , 'Games': Jsonify_List_Of_Games}
    return jsonify(Response), 200

@app.route('/All_RockPaperScissors_games_Winers')
def All_RockPaperScissors_games_Winers():
    ''''''
    List_Of_Games_Winers = Reading_Winers_From_DB()
    Jsonify_List_Of_Games_Winers = {} 
    for Game_Winers in List_Of_Games_Winers:
        id, player, name, = Game_Winers
        Jsonify_List_Of_Games_Winers[id] = {'Winer' : player , 'name' : name}
    Response = {'Status Code':200 , 'Winers': Jsonify_List_Of_Games_Winers}
    return jsonify(Response), 200

@app.route('/Change_User_Online_Status',methods=["GET", "POST"])
def Handle_Change_User_Online_Status():
    ''''''
    if request.method == 'POST': 
        Status = request.get_json()["Status"]
        UniqeID = request.get_json()["UniqeID"]
        Update_User_Status_In_Users_Table(UniqeID, Status)
        return "200"
    return "ERROR"

@app.route('/Create_User',methods=["GET", "POST"])
def Handle_Create_User():
    ''''''
    if request.method == 'POST': 
        name = request.get_json()["name"]
        Status = request.get_json()["Status"]
        Uniqeid = request.get_json()["Uniqeid"]
        writing_Users_to_database(Uniqeid, name, Status)
        return "200"
    return "ERROR"

@socketio.on('RockPaperScissorsAdded')
def Handle_RockPaperScissors_Added(game):
    ''''''
    socketio.emit('Rock Paper Scissors Added', game, broadcast=True)

@socketio.on('RockPaperScissorsChanged')
def Handle_RockPaperScissors_Changed(data):
    ''''''
    socketio.emit('Rock Paper Scissors Changed', data, broadcast=True)

@socketio.on('RockPaperScissorsGameEmitter')
def Handle_RockPaperScissors_Changed(data):
    ''''''
    #TODO
    List_Of_Games = Reading_Games_From_DB()
    Last_Game_ID, player1, player2, status = List_Of_Games[-1]
    writing_Winer_to_database(UniqeID, name,Last_Game_ID)
    pass

@app.route('/')
def index():
    #TODO 
    return render_template('index.html')

@app.route('/Join_To_RockPaperScissors_game',methods=["GET", "POST"])
def Handle_Join_To_RockPaperScissors_game():
    ''''''
    if request.method == 'POST':
        gameId = request.get_json()["gameId"]
        playerhash = request.get_json()["playerhash"]
        TXHASH = request.get_json()["paymentHash"]
        playerName = request.get_json()["playerName"]
        Value = request.get_json()["Value"]
        if Check_User_If_Online(playerhash) and Check_Payment_Hash(TXHASH,playerhash,Value):
            Update_Secound_Player_Address_In_Games_Table(gameId,playerhash,"started")
            Response = {'Event' : 'Join_To_RockPaperScissors' , 'gameId': gameId , 'playerhash' : playerhash , 'playerName' : playerName , 'status' : 'started'}
            return jsonify(Response), 200
        return "ERROR"

@app.route('/Create_RockPaperScissors_Game',methods=["GET", "POST"])
def Handle_Create_RockPaperScissors_Game():
    ''''''
    if request.method == 'POST':
        playerhash = request.get_json()["playerhash"]
        TXHASH = request.get_json()["paymentHash"]
        playerName = request.get_json()["playerName"]
        Value = request.get_json()["Value"]
        if Check_Payment_Hash(TXHASH,playerhash,Value):
            writing_Game_to_database(playerhash)
            List_Of_Games = Reading_Games_From_DB()
            Last_Game_ID, player1, player2, status = List_Of_Games[-1]
            Response = {'Event' : 'Create_RockPaperScissors' , 'gameId': Last_Game_ID , 'playerhash' : playerhash , 'playerName' : playerName , 'status' : 'pending'}
            return jsonify(Response), 200
        return "ERROR"


def Check_Payment_Hash(TXHASH,playerhash,Value):
    ''''''
    try:
        TX = w3.eth.get_transaction(str(TXHASH))
        TX_FROM = TX["from"]
        TX_VALUE = TX["value"]
        if TX_FROM == playerhash and TX_VALUE == Value:
            return True            
        else :
            return False
    except:
        return False

def Check_User_If_Online(playerhash):
    ''''''
    List_Of_Users = Reading_Users_From_DB()
    for User in List_Of_Users:
        id, UniqeID, name, Status = User
        if playerhash == UniqeID:
            if Status == "Connected":
                return True
            elif Status == "Disconnected" :
                return False

def Update_User_Status_In_Users_Table(UniqeID,status):
    ''''''
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'UPDATE users set status = "{status}" WHERE Uniqeid = "{UniqeID}";'
    cur.execute(qury)
    db.commit()
    db.close()

def Update_Secound_Player_Address_In_Games_Table(gameId,player,status):
    ''''''
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'UPDATE games SET player2 = "{player}" WHERE id = {gameId};'
    cur.execute(qury)
    db.commit()
    db.close()
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'UPDATE games SET status = "{status}" WHERE id = {gameId};'
    cur.execute(qury)
    db.commit()
    db.close()

def writing_Game_to_database(player1):
    ''''''
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'INSERT INTO Games (id, player1, player2, status) VALUES (null,"{player1}", "0x0000000000000000000000000000000000000000", "pending");'
    cur.execute(qury)
    db.commit()
    db.close()

def writing_Users_to_database(UniqeID, name, Status):
    ''''''
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'INSERT INTO Users (id, Uniqeid, name, status) VALUES  (null,"{UniqeID}","{name}","{Status}");'
    cur.execute(qury)
    db.commit()
    db.close()

def Reading_Games_From_DB():
    ''''''
    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM Games;")
    db.close()
    return cur.fetchall()

def Reading_Winers_From_DB():
    ''''''
    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM Winers;")
    db.close()
    return cur.fetchall()

def writing_Winer_to_database(UniqeID, name,id):
    ''''''
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'INSERT INTO Winers (id, Uniqeid, name) VALUES  (null,"{UniqeID}","{name}");'
    cur.execute(qury)
    db.commit()
    db.close()
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'UPDATE games SET status = "ended" WHERE id = {id};'
    cur.execute(qury)
    db.commit()
    db.close()

def Reading_Users_From_DB():
    ''''''
    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM Users;")
    db.close()
    return cur.fetchall()

def connect_to_database():
    ''''''
    db = pymysql.connect(host=config.MYSQL_HOST,
                       user=config.MYSQL_USER,
                       passwd=config.MYSQL_PASS,
                       db=config.MYSQL_DATABAS)
    return(db) 

if __name__ == '__main__':
    ''''''
    socketio.run(app, debug=True)