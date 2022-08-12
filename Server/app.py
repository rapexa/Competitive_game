#!/usr/bin/env

######################################## Libraries ########################################

from socket import socket
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_socketio import SocketIO ,join_room ,leave_room
from web3 import Web3

import hashlib
import pymysql
import config     #SERVER CONIG

########################################   Config   ########################################

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
socketio = SocketIO(app)
w3 = Web3(Web3.HTTPProvider(config.ETH))

########################################  REST API  ########################################

@app.route('/')
def index():
    '''This function return index.html page for more Document and Download'''
    return render_template('index.html')

@app.route("/ok")
def sys_check():
    '''This function check server is up or not...'''
    ret = {'Status code':'200','message':'Server is running...'}
    return jsonify(ret) , 200

@app.route('/All_RockPaperScissors_games')
def Handle_All_RockPaperScissors_games():
    '''This function return all Rock Paper Scissors games on database'''
    List_Of_Games = Reading_Games_From_DB()
    Jsonify_List_Of_Games = {} 
    for Game in List_Of_Games:
        id, player1, player2, status = Game
        Jsonify_List_Of_Games[id] = {'player1' : player1 , 'player2' : player2 , 'status' : status}
    Response = {'Status Code':200 , 'Games': Jsonify_List_Of_Games}
    return jsonify(Response), 200

@app.route('/All_RockPaperScissors_games_Winers')
def All_RockPaperScissors_games_Winers():
    '''This function return all Rock Paper Scissors game Winners on database'''
    List_Of_Games_Winers = Reading_Winers_From_DB()
    Jsonify_List_Of_Games_Winers = {} 
    for Game_Winers in List_Of_Games_Winers:
        id, player, name, = Game_Winers
        Jsonify_List_Of_Games_Winers[id] = {'Winer' : player , 'name' : name}
    Response = {'Status Code':200 , 'Winers': Jsonify_List_Of_Games_Winers}
    return jsonify(Response), 200

@app.route('/Change_User_Online_Status',methods=["GET", "POST"])
def Handle_Change_User_Online_Status():
    '''This function change one user connection status on database'''
    if request.method == 'POST': 
        Status = request.get_json()["Status"]
        UniqeID = request.get_json()["UniqeID"]
        Update_User_Status_In_Users_Table(UniqeID, Status)
        return "200"
    return "ERROR"

@app.route('/Create_User',methods=["GET", "POST"])
def Handle_Create_User():
    '''This function create one user on database'''
    if request.method == 'POST': 
        name = request.get_json()["name"]
        Status = request.get_json()["Status"]
        Uniqeid = request.get_json()["Uniqeid"]
        writing_Users_to_database(Uniqeid, name, Status)
        return "200"
    return "ERROR"

@app.route('/Create_Winner_Game',methods=["GET", "POST"])
def Handle_Winner_Game():
    '''This function write winners and equal games on database'''
    if request.method == 'POST': 
        name = request.get_json()["name"]
        Game_ID = request.get_json()["Game_ID"]
        Uniqeid = request.get_json()["Uniqeid"]
        Validate_hash = request.get_json()["Validate_hash"]
        Winner_status = request.get_json()["Winner_status"]
        if Winner_status == "Equal":
            writing_Winer_to_database("0x0000000000000000000000000000000000000000", "NULL",Game_ID)
            return "200"
        elif Winner_status == "Have_Winer":
            if hashlib.sha256(f"{Game_ID},{Uniqeid},{Validate_hash},Winner".encode("utf-8")).hexdigest() == Validate_hash: 
                writing_Winer_to_database(Uniqeid, name,Game_ID)
                return "200"
    return "ERROR"

@app.route('/Join_To_RockPaperScissors_game',methods=["GET", "POST"])
def Handle_Join_To_RockPaperScissors_game():
    '''This function change secound user address from nothing to one other user wallet address on database'''
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
    '''This function create one game on database'''
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

######################################## Socket.IO ########################################

@socketio.on('RockPaperScissorsGameEmitter')
def Handle_RockPaperScissors_GameEmitter(data):
    '''This function manage games, user on games and actions with socket'''
    Game_ID = data['Game_ID']   
    Playerhash = data['Playerhash']
    action = data['action']
    join_room(Game_ID)
    Res = {'Playerhash':Playerhash,'action':action}
    socketio.send(jsonify(Res), to=Game_ID)

@socketio.on('RockPaperScissorsGameEmitter_Leave')
def Handle_RockPaperScissors_GameEmitter(data):
    '''This function Leave one user from a room'''
    Game_ID = data['Game_ID']   
    Playerhash = data['Playerhash']
    Res = {'Playerhash':Playerhash,'Leave':"True"}
    socketio.send(jsonify(Res), to=Game_ID)
    leave_room(Game_ID)

@socketio.on('RockPaperScissorsAdded')
def Handle_RockPaperScissors_Added(game):
    '''This function broadcast adding Rock Paper Scissors game to games'''
    socketio.emit('Rock Paper Scissors Added', game, broadcast=True)

@socketio.on('RockPaperScissorsChanged')
def Handle_RockPaperScissors_Changed(data):
    '''This function broadcast status of Rock Paper Scissors game changed'''
    socketio.emit('Rock Paper Scissors Changed', data, broadcast=True)

######################################## Sys.Check ########################################

def Check_Payment_Hash(TXHASH,playerhash,Value):
    '''This function check TX hash for validate payment'''
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
    '''This function Check user is online and connected or not'''
    List_Of_Users = Reading_Users_From_DB()
    for User in List_Of_Users:
        id, UniqeID, name, Status = User
        if playerhash == UniqeID:
            if Status == "Connected":
                return True
            elif Status == "Disconnected" :
                return False

########################################   MYSQL  ########################################

def connect_to_database():
    '''This function make a connection with datebase'''
    db = pymysql.connect(host=config.MYSQL_HOST,
                       user=config.MYSQL_USER,
                       passwd=config.MYSQL_PASS,
                       db=config.MYSQL_DATABAS)
    return(db) 

def writing_Winer_to_database(UniqeID, name,id):
    '''This function write one game winner to database and update that game status to {ended}'''
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

def writing_Game_to_database(player1):
    '''This function create new game on database'''
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'INSERT INTO Games (id, player1, player2, status) VALUES (null,"{player1}", "0x0000000000000000000000000000000000000000", "pending");'
    cur.execute(qury)
    db.commit()
    db.close()

def writing_Users_to_database(UniqeID, name, Status):
    '''This function create new user on database'''
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'INSERT INTO Users (id, Uniqeid, name, status) VALUES  (null,"{UniqeID}","{name}","{Status}");'
    cur.execute(qury)
    db.commit()
    db.close()

def Reading_Games_From_DB():
    '''This function return all games from database'''
    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM Games;")
    db.close()
    return cur.fetchall()

def Reading_Winers_From_DB():
    '''This function return all winners from database'''
    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM Winers;")
    db.close()
    return cur.fetchall()

def Reading_Users_From_DB():
    '''This function return all users from database'''
    db = connect_to_database()
    cur = db.cursor()
    cur.execute("SELECT * FROM Users;")
    db.close()
    return cur.fetchall()

def Update_User_Status_In_Users_Table(UniqeID,status):
    '''This function update user connection status on database'''
    db = connect_to_database()
    cur = db.cursor()                       
    qury = f'UPDATE users set status = "{status}" WHERE Uniqeid = "{UniqeID}";'
    cur.execute(qury)
    db.commit()
    db.close()

def Update_Secound_Player_Address_In_Games_Table(gameId,player,status):
    '''This function add socound player address that join to one game on database'''
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

if __name__ == '__main__':
    '''Program controller that run jus once on start'''
    socketio.run(app, debug=True)