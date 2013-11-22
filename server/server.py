#!../framework/bin/python
from game import *
from flask import Flask, jsonify, abort
from player import *

app = Flask(__name__)

"""game list"""
_games_ = {}

"""player list"""
_players_ = {}

"""index of games"""
index = 0

def print_players():
	for item in _players_:
		print _players_[item].username + " " + _players_[item].ip
#only for testing
def print_games():
	for item in _games_:
		print _games_[item]

@app.route("/")
def hello():
	return "sono il server di anno domini\n"

@app.route('/createPlayer', methods = ['POST'])
def create_p():
	if not request.json or not 'username' in request.json:
		abort(400)
	new_p = Player(request.json['username'])
	if new_p.username not in _players_:
		_players_[new_p.username] = new_p
	else:
		abort(400)
	print_players()
	return new_p.to_json(), 201

@app.route('/createGame', methods = ['POST'])
def create_g():
	global index 
	if not request.json or not 'username' in request.json or not 'n_players' in request.json:
		abort(400)
	if _players_.has_key(request.json['username']):
		new_g = Game(index,_players_[request.json['username']],request.json['n_players'])
		_games_[index] = new_g
		index = index + 1
		print_games()
	else:
		abort(400)
	return new_g.to_json(), 201

@app.route('/joinGame', methods = ['POST'])
def join_g():
	if not request.json or not 'username' in request.json or not 'game_id' in request.json:
		abort(400)
	#Controllo che username e game_id sono stati passati correttamente
	req_id = int(request.json['game_id'])
	if not request.json['username'] in _players_ or not req_id in _games_:
		abort(400)
	#Modificare il metodo add_player della classe Player verificando che il giocatore non sia
	#gia presente nella lista
	player = _players_[request.json['username']]
	try:
		_games_[req_id].add_player(player)
		return "Game joined\n", 200
	except ValueError:
		abort(400)

if __name__ == '__main__':
	app.debug = True
	app.run()
