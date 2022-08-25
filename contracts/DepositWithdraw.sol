pragma solidity ^0.8.0;
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
contract DepositWithdraw is ReentrancyGuard, Ownable {

    event Deposit(address sender, uint256 value);


    function deposit() public payable {
        emit Deposit(_msgSender(), msg.value);
    }

    function withdraw(address payable _user, uint _value) external payable onlyOwner{
        _user.transfer(_value);
    }
}