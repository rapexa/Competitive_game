pragma solidity >=0.4.22 <0.9.0;

contract Game {
    mapping (uint => address[2]) gameToUser;
    mapping (uint => uint) gameToBet;
    mapping (uint => uint) gameUserCount;
    mapping (uint => uint) gameStatus;// gameNotExist=0, gameStart=1, gameRuning=2, gameEnd=3;
    bool equal;

    event StartGameEvent(address indexed user, uint game, uint status);
    event EndGameEvent(address indexed user, uint game, uint status);
    event EndGameEqualEvent(address indexed user1,address indexed user2, uint game, uint status);

    function startGame(uint _gameId)  public payable {
        require((gameUserCount[_gameId] == 0)  || (gameUserCount[_gameId] == 1 && gameToBet[_gameId] == msg.value));
        require((gameUserCount[_gameId] == 0)  || (gameToUser[_gameId][0] != msg.sender));

        gameStatus[_gameId] = gameUserCount[_gameId] + 1;

        gameToBet[_gameId] = msg.value;
        gameToUser[_gameId][gameUserCount[_gameId]] = msg.sender;
        gameUserCount[_gameId]++;

        emit StartGameEvent(msg.sender, _gameId, gameStatus[_gameId]);
    }

    function equalPlayer(
        uint _gameId,
         address payable _winner1, 
         address payable _winner2
        ) payable public returns(bool){

            require(gameToUser[_gameId][0] == _winner1 && gameToUser[_gameId][0] == _winner2
                ||
                gameToUser[_gameId][0] == _winner2 && gameToUser[_gameId][0] == _winner1 );

                _winner1.transfer(gameToBet[_gameId]);
                _winner2.transfer(gameToBet[_gameId]);
                gameStatus[_gameId]= 3;
                emit EndGameEqualEvent(_winner1,_winner2,_gameId,gameStatus[_gameId]);

                return  equal = true;

    }


    function endGame(uint _gameId, address payable _winner) payable external {
        require(!equal);   
        require(gameToUser[_gameId][0] == _winner || gameToUser[_gameId][1] == _winner );
        _winner.transfer(gameToBet[_gameId] * 2);
        gameStatus[_gameId]= 3;
        emit EndGameEvent(_winner, _gameId, gameStatus[_gameId]);
    }

    function returnPlayer(uint _game, uint _index) public view returns (address) {
        return gameToUser[_game][_index];
    }

}