#!/bin/bash
if test $# -ne 2; then  echo "Uso: $0 <porta> <id_game>";  exit 1;
fi
CMD="curl -i -X PUT http://localhost:$1/joinGame/$2"
eval $CMD
