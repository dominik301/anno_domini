#!../framework/bin/python
from game import *
from flask import Flask, jsonify, abort
from player import *

app = Flask(__name__)

"""game list"""
_games_ = []

"""player list"""
_players_ = {}

def print_players():
	for item in _players_:
		print _players_[item].username + " " + _players_[item].ip

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

if __name__ == '__main__':
	app.debug = True
	app.run()
