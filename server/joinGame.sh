#!/bin/bash
if test $# -ne 2; then  echo "Uso: $0 <username> <game_id>";  exit 1;
fi
CMD="curl -i -X PUT http://localhost:5000/joinGame/$1/$2"
eval $CMD
