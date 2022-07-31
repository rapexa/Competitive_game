pragma solidity ^0.8.15;
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract Game is ReentrancyGuard{
    mapping (uint => address[2]) gameToUser;
    mapping (uint => uint) gameToBet;
    mapping (uint => uint) gameUserCount;
    mapping (uint => uint) gameStatus;// gameNotExist=0, gameStart=1, gameRuning=2, gameEnd=3;

    event StartGameEvent(address indexed user, uint game, uint status);
    event EndGameEvent(address indexed user, uint game, uint status);

    

}