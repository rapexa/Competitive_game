// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "./security/ReentrancyGuard.sol";
import "./utils/Context.sol";
import "./utils/Address.sol";

contract PaymentProcess is ReentrancyGuard, Context {
    address public admin;
    address public owner;

    modifier onlyOwner() {
        require(
            _msgSender() == owner,
            "PaymentProcess: only admin can call it!"
        );
        _;
    }

    modifier onlyAdmin() {
        require(
            _msgSender() == admin,
            "PaymentProcess: only admin can call it!"
        );
        _;
    }

    event PaymentReceived(address from, uint256 indexed amount);
    event PaymentReleased(address indexed to, uint256 indexed amount);

    // the first admin and default admin is owner
    constructor() {
        owner = _msgSender();
        admin = owner;
    }

    // Deposit ether To Contract
    function DepositToContract() external payable onlyAdmin() {
        emit PaymentReceived(_msgSender(), msg.value);
    }

    // Withdraw ether From Contract
    function withdrawFromContract(address payable _receiver, uint _amount) external payable onlyAdmin {
        Address.sendValue(_receiver, _amount);
        emit PaymentReleased(_receiver, _amount);
    }

    function getBalanceOfContract() external view returns (uint256) {
        return address(this).balance;
    }

    // setting a new admin
    function setNewAdmin(address _admin) external onlyOwner {
        admin = _admin;
    }
}
