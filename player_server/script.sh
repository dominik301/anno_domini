#!/bin/bash
sh createPlayer.sh 5001 player1
sh createPlayer.sh 5002 player2
sh createPlayer.sh 5003 player3
sh createPlayer.sh 5004 player4
sh createGame.sh 5001 4
sh joinGame.sh 5002 0
sh joinGame.sh 5003 0
sh joinGame.sh 5004 0

