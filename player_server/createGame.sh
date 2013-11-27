#!/bin/bash
if test $# -ne 2; then  echo "Uso: $0 <porta> <n_players>";  exit 1;
fi
CMD="curl -i -X POST http://localhost:$1/createGame/$2"
eval $CMD
