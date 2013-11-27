#!/bin/bash
if test $# -ne 3; then  echo "Uso: $0 <porta> <username> <id_game>";  exit 1;
fi
CMD="curl -i -X PUT http://localhost:$1/joinGame/$2/$3"
eval $CMD
