#curl -i -X POST http://127.0.0.1:5001/createPlayer/pippo
#curl -i -X POST http://127.0.0.1:5001/createPlayer/pluto
#curl -i -X POST http://127.0.0.1:5001/createPlayer/paperino
#curl -i -X POST http://127.0.0.1:5001/createPlayer/paperone

#curl -i -X POST http://127.0.0.1:5001/createGame/pippo/2
#curl -i -X POST http://127.0.0.1:5001/createGame/pluto/5
#curl -i -X POST http://127.0.0.1:5001/createGame/paperino/6
#curl -i -X PUT http://127.0.0.1:5001/joinGame/paperone/0

#curl -i http://127.0.0.1:5000/gameList
#curl -i http://127.0.0.1:5000/playerList

curl -i -X POST http://127.0.0.1:5001/createPlayer/pippo
curl -i -X POST http://127.0.0.1:5001/createGame/2
curl -i -X POST http://127.0.0.1:5002/createPlayer/pluto
curl -i -X PUT http://127.0.0.1:5002/joinGame/0
