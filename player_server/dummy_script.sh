curl -i -X POST http://127.0.0.1:5001/createPlayer/pippo
curl -i -X POST http://127.0.0.1:5001/createPlayer/pluto
curl -i -X POST http://127.0.0.1:5001/createPlayer/paperino

curl -i -X POST http://127.0.0.1:5001/createGame/pippo/4
curl -i -X POST http://127.0.0.1:5001/createGame/pluto/5
curl -i -X POST http://127.0.0.1:5001/createGame/paperino/6
curl -i http://127.0.0.1:5000/gameList