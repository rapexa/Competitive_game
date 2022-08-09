# Competitive_game

[![LICENSE](https://img.shields.io/badge/LICENSE-MIT-green)](https://github.com/rapexa/Competitive_game/blob/main/LICENSE) 
[![Requirements](https://img.shields.io/badge/Requirements-See%20Here-orange)](https://github.com/rapexa/Competitive_game/blob/main/requirements.txt)
[![Todo](https://img.shields.io/badge/Todo-See%20Here-success)](https://github.com/rapexa/Competitive_game/blob/main/TODO.md)

Smart contract for a competitive game project focused on depositing the prize to the winner with cross platform proffesional Flutter app running RockPaperScissors.

## Technologies

- Solidity
- Truffle
- Flutter
- Flask
- Python
- Mysql
- SocketIO
- Rest api

## How to run
1. Install all Requirements for this project.
2. Clone the project `git clone https://github.com/rapexa/Competitive_game && cd Competitive_game`

CREATE DATABASE CP_GAME;

CREATE USER 'DEVELOPERUSER'@'localhost' IDENTIFIED BY 'DEVELOPERPASS';

GRANT ALL PRIVILEGES ON CP_GAME.* TO 'DEVELOPERUSER'@'localhost';

USE CP_GAME;

DROP TABLE IF EXISTS Games;

DROP TABLE IF EXISTS Users;

CREATE TABLE Games (id INT NOT NULL AUTO_INCREMENT, player1 VARCHAR(260),player2 VARCHAR(260),status VARCHAR(50), PRIMARY KEY(id));

CREATE TABLE Users (id int NOT NULL AUTO_INCREMENT, Uniqeid VARCHAR(260),name VARCHAR(100),status VARCHAR(50), PRIMARY KEY(id));

CREATE TABLE Winers (id int NOT NULL AUTO_INCREMENT, Uniqeid VARCHAR(260), name VARCHAR(100), PRIMARY KEY(id));