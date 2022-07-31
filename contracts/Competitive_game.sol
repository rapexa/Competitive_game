pragma solidity ^0.8.15;
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract Game is ReentrancyGuard{
    mapping (uint => address[2]) gameToUser;
    mapping (uint => uint) gameToBet;
    mapping (uint => uint) gameUserCount;
    mapping (uint => uint) gameStatus;// gameNotExist=0, gameStart=1, gameRuning=2, gameEnd=3;

    event StartGameEvent(address indexed user, uint game, uint status);
    event EndGameEvent(address indexed user, uint game, uint status);

function startGame(uint _gameId)  public payable nonReentrant {
        require((gameUserCount[_gameId] == 0)  || (gameUserCount[_gameId] == 1 && gameToBet[_gameId] == msg.value));
        require((gameUserCount[_gameId] == 0)  || (gameToUser[_gameId][0] != msg.sender));

        gameStatus[_gameId] = gameUserCount[_gameId] + 1;

        gameToBet[_gameId] = msg.value;
        gameToUser[_gameId][gameUserCount[_gameId]] = msg.sender;
        gameUserCount[_gameId]++;

        emit StartGameEvent(msg.sender, _gameId, gameStatus[_gameId]);
    }

    function endGame(uint _gameId, address payable _winner) payable external {
        require(gameToUser[_gameId][0] == _winner || gameToUser[_gameId][1] == _winner );
        _winner.transfer(gameToBet[_gameId] * 2);
        gameStatus[_gameId]= 3;
        emit EndGameEvent(_winner, _gameId, gameStatus[_gameId]);

    }

    function returnPlayer(uint _game, uint _index) public view returns (address) {
        return gameToUser[_game][_index];
    }

}