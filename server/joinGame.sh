#!/bin/bash
CMD="curl -i -H \"Content-Type: application/json\" -X POST -d '{\"game_id\":\"$1\"}' http://localhost:5000/joinGame"
eval $CMD
