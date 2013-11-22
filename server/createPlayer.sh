#!/bin/bash
CMD="curl -i -H \"Content-Type: application/json\" -X POST -d '{\"username\":\"$1\"}' http://localhost:5000/createPlayer"
eval $CMD

