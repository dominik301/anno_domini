#!../framework/bin/python
import sys
from game import *
from flask import Flask, jsonify, abort,redirect,request
from player import *
import json

app = Flask(__name__)

"""game list"""
_games_ = {}

"""player list"""
_players_ = {}

"""index of games"""
index = 0

#only for testing
@app.route("/playerList", methods = ['GET'])
def get_players():
	players_dict = dict((_players_.get(player).username, _players_.get(player).ip, _players_.get(player).porta) for player in _players_)
	return jsonify(players_dict)

@app.route("/gameList", methods = ['GET'])
def get_games():
	game_list = [] 
	index = 0
	if len(_games_) == 0 :
		return json.dumps(game_list, default=lambda o: o.__dict__)
	for game in _games_:
		creator = _games_.get(game).creator.username
		player_number = _games_.get(game).player_n
		new_g = Game(index,_games_.get(game).p_list[0], player_number)
		game_list.append(new_g)
		index = index + 1
	print game_list
	return json.dumps(game_list, default=lambda o: o.__dict__)

#only for testing
@app.route("/printGames", methods = ['GET'])
def print_games():
	for item in _games_:
		print _games_[item]
	return "",200

@app.route("/")
def hello():
	return "sono il server di anno domini\n"

@app.route('/createPlayer/<string:username>/<int:porta>', methods = ['POST'])
def create_p(username,porta):
	new_p = Player(username, str(request.remote_addr), porta)
	if new_p.username not in _players_:
		_players_[new_p.username] = new_p
	else:
		return "Username already chosen\n", 400
	return "Registrato", 201

@app.route('/createGame/<string:username>/<int:n_players>', methods = ['POST'])
def create_g(username, n_players):
	global index
	if index == 1:
		return "Project limitation: maximum one game!", 400 
	if username in _players_:
		try:
			new_g = Game(index, _players_[username], n_players)
		except PlayersNumberRangeException:		
			return "Wrong number of players\n", 400
		except CreatorNotFoundException:
			return "Creator non found\n", 400
		_games_[index] = new_g
		index = index + 1
	else:
		return "Unknown username\n", 400
	return str(index-1), 201 

@app.route('/joinGame/<string:username>/<int:game_id>', methods = ['PUT'])
def join_g(username, game_id):
	#Controllo che username e game_id siano stati passati correttamente
	if username not in _players_ or game_id not in _games_:
		return "Player or game not found\n", 400
	player = _players_[username]
	game = _games_[game_id]
	try:
		game.add_player(player)
	except PlayersNumberReachedException:
		return "Number of players already reached\n", 400
	except UserSubscriptionException:
		return "User is already subscripted\n", 400
	if game.player_n == len(game.p_list):
		for i in game.p_list:
			print i.ip
			url = "http://"+i.ip+":"+str(i.porta)+"/startGame"
			headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
			r = requests.put(url, json.dumps(game.p_list, default=lambda o: o.__dict__), headers=headers)
	return "Game joined\n",200

@app.route('/unsubscribe/<string:username>/<int:game_id>', methods = ['DELETE'])
def unsubscribe(username, game_id):
	#Controllo che username e game_id siano stati passati correttamente
	if username not in _players_ or game_id not in _games_:
		return "Player or game not found", 400
	try:
		_games_[game_id].remove_player(_players_[username])
		print _games_[game_id].p_list
	except UserNotFoundException:
		return "User not subscripted to the specified game", 400
	except CreatorUnsubscriptionException:
		return "Creator cannot be unsubscribed", 400
	return "User is not partecipating anymore", 200

if __name__ == '__main__':
	app.debug = True
	if len(sys.argv) == 1:
		app.run("127.0.0.1", threaded = True)
	elif len(sys.argv) == 2:
		app.run(sys.argv[1], threaded = True)
	else:
		print "Usage:", sys.argv[0], "<public IP>"
		exit(1)
