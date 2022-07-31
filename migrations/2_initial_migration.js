const Game = artifacts.require("Game");

module.exports = function (deployer) {
  deployer.deploy(Game);
};
