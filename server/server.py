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
		return "username not in json request or n_players not in json request\n", 400
	username = request.json['username']
	if _players_.has_key(username):
		new_g = Game(index,_players_[username],request.json['n_players'])
		_games_[index] = new_g
		index = index + 1
		_players_[username].subscribed_games = 1
		print_games()
	else:
		abort(400)
	return new_g.to_json(), 201

@app.route('/joinGame/<string:username>/<int:game_id>', methods = ['PUT'])
def join_g(username, game_id):
	#Controllo che username e game_id sono stati passati correttamente
	if username not in _players_ or game_id not in _games_:
		abort(400)
	player = _players_[username]
	try:
		_games_[game_id].add_player(player)
	except ValueError:
		abort(400)
	if _games_[game_id].player_n == len(_games_[game_id].p_list):
		_games_[game_id].start_game()
		return "la partita puo iniziare\n",200		
	return "Game joined\n", 200

if __name__ == '__main__':
	app.debug = True
	app.run("172.16.30.1")
	#app.run()