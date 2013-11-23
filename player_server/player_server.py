#!../framework/bin/python
import requests
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
	return "sono il server_player\n"

@app.route('/createPlayer', methods = ['POST'])
def create_p():
	return "permette al giocatore di iscriversi al server di anno domini"

@app.route('/createGame', methods = ['POST'])
def create_g():
	return "permette ad un giocatore di creare una partita"

@app.route('/joinGame/<string:username>/<int:game_id>', methods = ['PUT'])
def join_g(username,game_id):
	return requests.put("http://localhost:5000/joinGame/username/game_id")

r = requests.get('http://localhost:5000/')
print(r.text)