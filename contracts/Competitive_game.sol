// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;
import "./ReentrancyGuard.sol";

contract Game is ReentrancyGuard{
    mapping (uint => address payable[2]) gameToUser;// mapp gameId to two user address
    mapping (uint => uint) gameToBet;// mapp gameId to user's value
    mapping (uint => uint) gameUserCount;// mapp gameId to number of user in the game
    mapping (uint => uint) gameStatus;// gameNotExist=0, gameStart=1, gameRuning=2, gameEndWithWinner=3, gameEndWithTie=4;

    event StartGameEvent(address indexed user, uint game, uint status);
    event EndGameWithWinner(address indexed user, uint game, uint status);
    event EndGameWithTie(uint game, uint status);

function startGame(uint _gameId)  public payable nonReentrant {
        //Game start if the user is the first user in the game or if user is the second one, he's value should be equal to first user value
        require((gameUserCount[_gameId] == 0)  || (gameUserCount[_gameId] == 1 && gameToBet[_gameId] == msg.value));
        //Game start if the user is the first user in the game or if user is the second one, he's address should'nt be equal to first user address
        require((gameUserCount[_gameId] == 0)  || (gameToUser[_gameId][0] != msg.sender));
        
        // if(gameUserCount[_gameId]==0){
        //     gameStatus[_gameId]=1
        //     }
        // else if(gameUserCount[_gameId]==1){
        //     gameStatus[_gameId]=2
        //     }
        gameStatus[_gameId] = gameUserCount[_gameId] + 1;

        gameToBet[_gameId] = msg.value;//User value save in gameToBet 
        //The addresses of the users are placed in the array respectivly, the first user in the first element([0]), the second user in the second element([1])
        gameToUser[_gameId][gameUserCount[_gameId]] = payable(msg.sender);
        gameUserCount[_gameId]++;//increase number of user in the game 

        emit StartGameEvent(msg.sender, _gameId, gameStatus[_gameId]);
    }

    function endGameWithWinner(uint _gameId, address payable _winner) payable external {
        require(gameStatus[_gameId] == 2); // check that game running with two user and the result is'nt tie
        require(gameToUser[_gameId][0] == _winner || gameToUser[_gameId][1] == _winner );// check that the winner address be in the user address
        _winner.transfer(gameToBet[_gameId] * 2); // winner gives the value of two user
        gameStatus[_gameId]= 3;//gameEndWithWinner=3
        emit EndGameWithWinner(_winner, _gameId, gameStatus[_gameId]);

    }

    function endGameWithTie(uint _gameId) payable external {
        require(gameStatus[_gameId] == 2); // check that game running with two user and no one is winner
        gameToUser[_gameId][0].transfer(gameToBet[_gameId]);
        gameToUser[_gameId][1].transfer(gameToBet[_gameId]);
        gameStatus[_gameId]= 4;//gameEndWithTie=4
        emit EndGameWithTie(_gameId, gameStatus[_gameId]);
    }

    function returnPlayer(uint _game, uint _index) public view returns (address) {
        return gameToUser[_game][_index];
    }

}