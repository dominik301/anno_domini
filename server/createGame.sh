#!/bin/bash
if test $# -ne 2; then  echo "Uso: $0 <username> <n_players>";  exit 1;
fi
CMD="curl -i -H \"Content-Type: application/json\" -X POST -d '{\"username\":\"$1\",\"n_players\":$2}' http://localhost:5000/createGame"
eval $CMD
