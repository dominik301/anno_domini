#!/bin/bash
if test $# -ne 5; then  echo "Uso: $0 <porta_1> <porta_2> <porta_3> <porta_4> <porta_5>";  exit 1;
fi
sh createPlayer.sh $1 player1
sh createPlayer.sh $2 player2
sh createPlayer.sh $3 player3
sh createPlayer.sh $4 player4
sh createPlayer.sh $5 player5
sh createGame.sh $1 5
sh joinGame.sh $2 0
sh joinGame.sh $3 0
sh joinGame.sh $4 0
sh joinGame.sh $5 0

