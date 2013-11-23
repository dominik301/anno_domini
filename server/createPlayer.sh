#!/bin/bash
if test $# -ne 1; then  echo "Uso: $0 <username>";  exit 1;
fi
CMD="curl -i -X POST http://localhost:5000/createPlayer/$1"
eval $CMD
