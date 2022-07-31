// SPDX-License-Identifier: MIT
pragma solidity  ^0.8.15;
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

import "@openzeppelin/contracts/access/Ownable.sol";


contract gettingwinner is ReentrancyGuard, Ownable {

    mapping(uint256 => gameData) private gameDetails;
    //we do not use the initial this in constructor, beacause it may change in deploying contract (that can be attack)
    uint256 numberGames=0;

    address public referee;

    uint256 public pay = 1 ether;

    //adddddddddddddddd

     bool public closed = false;

     uint256 public startTime;

    uint256 public endTime;

    modifier ended() {
  require(block.timestamp >= endTime || closed == true);

  _;
 }

  modifier notClosed() {
  require(closed  == false);

  _;
 }

 function started() public view returns (bool) {
  return block.timestamp >= startTime;
 }

 function endGame() onlyOwner public {
  closed = true;
 }


 //addddddddddd

    modifier refereeVote() {
  require(msg.sender  == referee);

  _;
 }

    constructor(address _referee) {

    referee = _referee;
 }

    struct gameData{
        address  gamer1;
        address  gamer2;
        uint256 fund;
    }
    event showAddress(address addr, uint256 id);
    event createGameLog(address addr, uint256 id,uint256 money);
    event showAllDetails(address firstGamer,address secoundGamer,uint256 money);

    //we use the nonReentrant
    function createGame(address payable _gamer2) public payable notClosed nonReentrant{
        require(msg.value == gameDetails[pay].fund);

         gameDetails[pay].gamer2 = msg.sender;

        gameDetails[numberGames]=gameData({
            gamer1:msg.sender,
            gamer2: _gamer2,
            fund:msg.value
        });

        startTime = block.timestamp;

        emit createGameLog(msg.sender, numberGames, msg.value);

        emit showAllDetails(msg.sender, _gamer2, gameDetails[pay].fund);
        //we can use the openzeppline for adding safe but in version 8 to up no need to it
        //we used ++i instead i++ for less gas
        ++numberGames;
    }

    //we should find that the addr is an gamer address or no, just gamers should call this
    //the addr is coming from site, so it should valid
    function whoWinner(address payable addr, uint256 id) payable ended  refereeVote external {
        require(gameDetails[id].gamer1 == addr || gameDetails[id].gamer2 == addr);
        emit showAddress(addr, pay);
        addr.transfer(gameDetails[id].fund);
        endTime = block.timestamp;
    }
}