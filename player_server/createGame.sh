#!/bin/bash
if test $# -ne 3; then  echo "Uso: $0 <porta> <username> <n_players>";  exit 1;
fi
CMD="curl -i -X POST http://localhost:$1/createGame/$2/$3"
eval $CMD
