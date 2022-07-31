// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Context.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Game is ReentrancyGuard, Ownable {
    using Counters for Counters.Counter; // using counters labrary for increament ids
    Counters.Counter public gameId;

    struct GameInfo {
        uint256 _gameId;
        uint256 amountTokenLoked;
        address host;                       //host who create game, every address can create game only for once
        address gust;                       //gust who join the game, every address can join the game only for once
        bool started;                       //player1 created new game and paied some tokens
        bool locked;                        //player2 joined the game and paied some tokens
        bool opened;                        //winner and loser are known
        bool ended;                         //winner widthraw tokens and hasStarted[player1] = false
    }

    mapping(uint256 => GameInfo) private everyGameInfo;                         // evertGameInfo[_id] = GameInfo...
    mapping(address => bool) private hasStarted;                                // hasStarted[player1] = false
    mapping(address => bool) private hasJoined;                                 // hasJoined[player2] = false
    mapping(uint256 => mapping(address => bool)) public isWinner;               // isWinner[gameId[player1]] = false
    mapping(address => mapping(uint256 => uint256)) private balancePlayers;     // balacePlayers[player1][2] = 1000...

    // emit event after creating a game
    event GameCreated(
        uint256 indexed gameId,
        uint256 amountTokenLoked,
        address host,
        address gust,
        bool started,
        bool locked,
        bool opened,
        bool ended
    );

    // balace of contract
    function getBalance() external view onlyOwner returns (uint256) {
        return address(this).balance;
    }

    // state of every games with specefic id. returns struct
    function gameState(uint256 _id) external view returns (GameInfo memory) {
        return everyGameInfo[_id];
    }

    // start a game. player starts game with his address.
    function createGame(address _player1) external payable nonReentrant {
        require(
            _msgSender() == _player1,
            "Game: msg sender not equal address palyer"
        );
        require(
            hasStarted[_player1] == false,
            "Game: this address has started a game before!"
        );
        require(
            msg.value > 0,
            "Game: amount token is less than or equal zero!"
        );

        gameId.increment();
        uint256 currentId = gameId.current();                       // current id is game id
        balancePlayers[_player1][currentId] = msg.value;            // update balance player for this game id
        everyGameInfo[currentId] = GameInfo(                        // set state for game id
            currentId,
            msg.value,
            payable(_player1),
            address(0),
            true,
            false,
            false,
            false
        );

        hasStarted[_player1] = true;            

        emit GameCreated(
            currentId,
            msg.value,
            _player1,
            address(0),
            true,
            false,
            false,
            false
        );
    }

    // player1 can cancel the game when he wants, if nobody join in his game.
    function cancelTheGame(uint256 _id) external {
        require(
            everyGameInfo[_id].host == _msgSender(),
            "Game: your are not host of this game!"
        );
        require(
            everyGameInfo[_id].started == true &&
            everyGameInfo[_id].gust == address(0),
            "Game: you can not cancel the game because the game has started!"
        );


        delete everyGameInfo[_id];
        hasStarted[_msgSender()] = false;
        uint256 amount = balancePlayers[_msgSender()][_id];
        balancePlayers[_msgSender()][_id] = 0;
        payable(_msgSender()).transfer(amount);
    }

    function joinGame(uint256 _id, address _player2)
        external
        payable
        nonReentrant
    {
        require(
            _msgSender() == _player2,
            "Game: msg sender not equal address palyer"
        );
        require(
            hasStarted[_player2] == false,
            "Game: this address has started before, so can not join now!"
        );
        require(
            hasJoined[_player2] == false,
            "Game: this address has joined a game, so can not join now!"
        );
        require(
            msg.value == everyGameInfo[_id].amountTokenLoked,
            "Game: amount token is not equal with token that locked by player1!"
        );
        require(
            everyGameInfo[_id].locked == false,
            "Game: this game has locked before!"
        );
        require(
            everyGameInfo[_id].started == true &&
                everyGameInfo[_id].gust == address(0),
            "Game: this game does not have place or does not started!"
        );

        hasJoined[_player2] = true;
        balancePlayers[_player2][_id] += msg.value;
        everyGameInfo[_id].amountTokenLoked += msg.value;
        everyGameInfo[_id].locked = true;
        everyGameInfo[_id].gust = _player2;
    }

    // bug: check valid game
    //owner can determine the winner of curse this function is not correct in logical :)
    function chooseWinner(
        uint256 _id,
        address winner,
        address loser
    ) external onlyOwner {
        require(
            everyGameInfo[_id].locked == true,
            "Game: this game does not have place or does not started!"
        );
        require(
            everyGameInfo[_id].host == winner ||
                everyGameInfo[_id].gust == winner,
            "Game: winner is not in this game!"
        );
        require(
            everyGameInfo[_id].host == loser ||
                everyGameInfo[_id].gust == loser,
            "Game: loser is not in this game!"
        );

        isWinner[_id][winner] = true;
        everyGameInfo[_id].opened = true;

        if (
            everyGameInfo[_id].host == winner &&
            everyGameInfo[_id].host == loser
        ) {
            playersExitedFromTheGame(winner, loser);
        }
    }

    function withdraw(uint256 _id) external nonReentrant {
        require(
            everyGameInfo[_id].opened == true,
            "Game: this game does not oppened yet!"
        );
        require(
            everyGameInfo[_id].host == _msgSender() ||
                everyGameInfo[_id].gust == _msgSender(),
            "Game: this address has not in this game!"
        );
        require(
            isWinner[_id][_msgSender()] == true,
            "Game: you are not winner!"
        );

        everyGameInfo[_id].ended = true;
        uint256 amount = everyGameInfo[_id].amountTokenLoked;
        balancePlayers[_msgSender()][_id] = 0;
        payable(_msgSender()).transfer(amount);
    }

    //show the games that started and dont have gust
    function showAllStartedGames() external view returns (GameInfo[] memory) {
        uint256 gameCount = gameId.current();
        uint256 gamesCountForShowing = 0;
        uint256 currentIndex = 0;

        for (uint256 i = 0; i < gameCount; i++) {
            if (
                everyGameInfo[i + 1].gust == address(0) &&
                everyGameInfo[i + 1].host != address(0)
            ) {
                gamesCountForShowing += 1;
            }
        }

        GameInfo[] memory games = new GameInfo[](gamesCountForShowing);

        for (uint256 i = 0; i < gameCount; i++) {
            if (everyGameInfo[i + 1].gust == address(0)) {
                uint256 currentI = i + 1;
                GameInfo storage currentGame = everyGameInfo[currentI];
                games[currentIndex] = currentGame;
                currentIndex += 1;
            }
        }
        return games;
    }

    function playersExitedFromTheGame(address host, address gust) internal {
        hasStarted[host] = false;
        hasJoined[gust] = false;
    }
}
