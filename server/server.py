#!../framework/bin/python
from game import *
from flask import Flask
from flask import jsonify
from player import *

app = Flask(__name__)

"""game list"""
_games_ = []

"""player list"""
_players_ = []

@app.route("/")
def hello():
	return "sono il server di anno domini\n"

@app.route('/createPlayer', methods = ['POST'])
def create_p():
	if not request.json or not 'player_name' in request.json:
		abort(400)
	new_p = Player(request.json['player_name'])
	_players_.append(new_p)
	print _players_
	return new_p.to_json(), 201

if __name__ == '__main__':
	app.debug = True
	app.run()