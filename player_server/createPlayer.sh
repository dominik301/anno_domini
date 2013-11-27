#!/bin/bash
if test $# -ne 2; then  echo "Uso: $0 <porta> <username>";  exit 1;
fi
CMD="curl -i -X POST http://localhost:$1/createPlayer/$2"
eval $CMD
