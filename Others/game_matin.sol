// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;
import "./security/ReentrancyGuard.sol";
import "./utils/Context.sol";

contract MyContract is ReentrancyGuard, Context {
    address public admin;
    address public owner;

    mapping(uint256 => uint256) minimumBet;                         // minimumBet[gameId] = 1 ether
    mapping(uint256 => uint256) balanceGame;                        // balanceGame[gameId] = 2 ether
    mapping(address => mapping(uint256 => uint256)) balancePlayer;  // balancePlayer[playerAddress][gameId] = 1 ether
    mapping(address => mapping(uint256 => bool)) isWinner;          // isWinner[playerAddress][gameId] = false
    mapping(uint256 => bool) isGameTied;                            // isGameTied[gameId] = false

    event GameStarted(address starter, uint256 gameId);
    event RewardGotten(address receiver, uint256 amount);
    event BetDeposited(address sender, uint256 amount);

    modifier onlyOwner() {
        require(_msgSender() == owner, "MyContract: only admin can call it!");
        _;
    }

    modifier onlyAdmin() {
        require(_msgSender() == admin, "MyContract: only admin can call it!");
        _;
    }

    modifier isSender(address sender) {
        require(
            _msgSender() == sender,
            "MyContract: this address is not msg sender!"
        );
        _;
    }

    // the first admin and default admin is owner
    constructor() {
        owner = _msgSender();
        admin = owner;
    }

    // id must be random number
    function startGame(address _player, uint256 _gameId)
        external
        payable
        isSender(_player)
        nonReentrant
    {
        require(msg.value > 0, "MyContract: value must more than zero!");

        minimumBet[_gameId] = msg.value;
        balancePlayer[_player][_gameId] = msg.value;
        balanceGame[_gameId] = msg.value;

        emit GameStarted(_player, _gameId);
    }

    // players deposit thir tokens sperated(the necessary condition
    // is amount of tokens checkes in web2)
    function depositBet(address _player, uint256 _gameId)
        external
        payable
        nonReentrant
        isSender(_player)
    {
        require(
            msg.value >= minimumBet[_gameId],
            "MyContract: the value has to more than minimumBet for starting this game!"
        );

        balancePlayer[_player][_gameId] = msg.value;
        balanceGame[_gameId] += msg.value;

        emit BetDeposited(_player, msg.value);
    }

    // setting a winner by admin from back-end. back-end pass address
    // as arguman, by calling this function with private key of admin.
    function setNewWinner(address payable _winner, uint256 _gameId)
        external
        onlyAdmin
    {
        isWinner[_winner][_gameId] = true;
        balancePlayer[_winner][_gameId] = balanceGame[_gameId];
        balanceGame[_gameId] = 0;
    }

    // winner withdraws all Reward of the game
    function withdrawReward(address _winner, uint256 _gameId)
        external
        payable
        isSender(_winner)
        nonReentrant
    {
        require(
            isWinner[_winner][_gameId] == true,
            "MyContract: only winners can call it!"
        );

        (bool sent, ) = _winner.call{value: balancePlayer[_winner][_gameId]}(
            ""
        );

        require(sent, "MyContract: withdrawReward has failed!");

        delete isWinner[_winner][_gameId];

        emit RewardGotten(_winner, balancePlayer[_winner][_gameId]);
    }

    // setting a new admin
    function setNewAdmin(address _admin) external onlyOwner {
        admin = _admin;
    }

    function contractBalance() external view onlyOwner returns (uint256) {
        return address(this).balance;
    }

    function getPlayersBalance(address _player, uint256 _gameId)
        external
        view
        returns (uint256)
    {
        return balancePlayer[_player][_gameId];
    }

    function getGameBalance(uint256 _gameId) external view returns (uint256) {
        return balanceGame[_gameId];
    }

    function isAddresWinner(address _player, uint256 _gameId)
        external
        view
        returns (bool)
    {
        return isWinner[_player][_gameId];
    }
}

// mapping(address => mapping(address => mapping(uint256 => uint256))) balancePlayer; // balancePlayer[playerAddress][tokenAddress][gameId] = 1 ether
