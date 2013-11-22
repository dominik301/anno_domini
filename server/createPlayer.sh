#!/bin/bash
if test $# -ne 1; then  echo "Uso: $0 <username>";  exit 1;
fi

CMD="curl -i -H \"Content-Type: application/json\" -X POST -d '{\"username\":\"$1\"}' http://localhost:5000/createPlayer"
eval $CMD

