// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract MoneyPool {

    struct Deposit {
        address sender;
        uint256 amount;
        uint256 timestamp;
    }

    mapping(string => Deposit[]) public  pool;
    mapping(address => bool) private playerAlreadyInAGame;

    function GenesisPlayer(string calldata gameId) public payable {
        require(pool[gameId].length == 0); // check game exist or not
        require(!playerAlreadyInAGame[msg.sender]); // check player already in a game or not
        pool[gameId].push(Deposit({sender: msg.sender, amount: msg.value, timestamp: block.timestamp}));
        emit Log(msg.sender, "Game created successfully");
    }

    function OtherPlayer(string calldata gameId) public payable {
        require(pool[gameId]/*Genesis Record*/[0].amount == msg.value); // check amount player 2 is equal player 1 or not
        require(!playerAlreadyInAGame[msg.sender]); // check player already in a game or not
        pool[gameId].push(Deposit({sender: msg.sender, amount: msg.value, timestamp: block.timestamp}));
        emit Log(msg.sender, "You joined the game");
    }

    function withdrawToWin(address payable winnerAddress, string calldata gameId) payable external {
        uint256 totalAmount;
        bool winnerAddressIsInPlayerPool = false;
        for(uint8 i = 0; i < pool[gameId].length; i++){
            if(pool[gameId][i].sender == winnerAddress){
                winnerAddressIsInPlayerPool = true;
                playerAlreadyInAGame[winnerAddress] = false;
            }
            playerAlreadyInAGame[pool[gameId][i].sender] = false;
            uint256 amount = pool[gameId][i].amount;
            totalAmount = totalAmount + amount;
        }
        if(winnerAddressIsInPlayerPool){
            require(totalAmount > 0);
            winnerAddress.transfer(totalAmount);
            delete pool[gameId];
            emit Log(msg.sender, "You have won the game!");
        }
    }
    event Log(address indexed sender, string message);
}


//changelog
//check a player already in the game or not
