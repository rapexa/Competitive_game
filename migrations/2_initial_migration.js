const ReentrancyGuard = artifacts.require("ReentrancyGuard");

module.exports = function (deployer) {
  deployer.deploy(ReentrancyGuard);
};