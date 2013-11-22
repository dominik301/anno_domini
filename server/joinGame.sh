#!/bin/bash
if test $# -ne 2; then  echo "Uso: $0 <username> <game_id>";  exit 1;
fi
CMD="curl -i -H \"Content-Type: application/json\" -X POST -d '{\"username\":\"$1\",\"game_id\":\"$2\"}' http://localhost:5000/joinGame"
eval $CMD
