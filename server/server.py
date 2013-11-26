#!../framework/bin/python
from game import *
from flask import Flask, jsonify, abort,redirect,request
from player import *

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
	players_dict = dict((_players_.get(player).username, _players_.get(player).ip) for player in _players_)
	return jsonify(players_dict)
	return "",200

@app.route("/gameList", methods = ['GET'])
def get_games():
	return json.dumps(_games_)

#only for testing
@app.route("/printGames", methods = ['GET'])
def print_games():
	for item in _games_:
		print _games_[item]
	return "",200

@app.route("/")
def hello():
	return "sono il server di anno domini\n"

@app.route('/createPlayer/<string:username>', methods = ['POST'])
def create_p(username):
	new_p = Player(username, str(request.remote_addr))
	if new_p.username not in _players_:
		_players_[new_p.username] = new_p
	else:
		return "Username already chosen\n", 400
	return "", 201

@app.route('/createGame/<string:username>/<int:n_players>', methods = ['POST'])
def create_g(username, n_players):
	global index 
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
	return str(index), 201 

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
		port = 5001
		for i in game.p_list:
			url = "http://"+i.ip+":"+str(port)+"/startGame"
			headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
			r = requests.put(url, json.dumps(game.p_list, default=lambda o: o.__dict__), headers=headers)
			port = port + 1 
		return "Game joined\n",200
	else :
		return "Game joined\n", 200

@app.route('/unsubscribe/<string:username>/<int:game_id>', methods = ['DELETE'])
def unsubscribe(username, game_id):
	#Controllo che username e game_id siano stati passati correttamente
	if username not in _players_ or game_id not in _games_:
		return "Player or game not found", 400
	try:
		_games_[game_id].remove_player(_players_[username])
	except UserNotFoundException:
		return "User not subscripted to the specified game", 400
	except CreatorUnsubscriptionException:
		return "Creator cannot be unsubscribed", 400
	return "User is not partecipating anymore", 200

if __name__ == '__main__':
	app.debug = True
	app.run('127.0.0.1', threaded = True)
