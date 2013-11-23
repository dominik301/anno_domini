#!/bin/bash
if test $# -ne 2; then  echo "Uso: $0 <username> <n_players>";  exit 1;
fi
CMD="curl -i -X POST http://localhost:5000/createGame/$1/$2"
eval $CMD
