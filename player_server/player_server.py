#!../framework/bin/python
import requests
import json
import random
from flask import Flask, jsonify, request, abort
from game_card import *
from deck import *

#nome con cui mi registro al server
my_player_name = ""

#mazzo
deck = Deck

#le carte sul tavolo
table = []

#id della partita a cui si sta partecipando
joined_game_id = -1

#lista di giocatori 
players = {}

app = Flask(__name__)
server_ip = "127.0.0.1"
server_port = 5000

#recupera la lista dei giocatori iscritti alla partita con joined_game_id e riempie il dict players
def get_players():
	global players
	if joined_game_id != -1:
		req = requests.post("http://"+server_ip+":5000/"+str(joined_game_id)+"/players")
		if not req.json:
			abort(400)
		print req.json
		players = req
	else:
		raise ValueError("joined_game_id == 1")

@app.route("/")
def hello():
	return "sono il server_player ip: " + server_ip + " porta: " + str(server_port) + "\n"

@app.route('/createPlayer/<string:username>', methods = ['POST'])
def create_p(username):
	if username != "":
		req = requests.post("http://"+server_ip+":5000/createPlayer/"+username)
		my_player_name = username
		return "", req.status_code
	else:
		return "",400

@app.route('/createGame/<string:username>/<int:n_players>', methods = ['POST'])
def create_g(username, n_players):
	if username != "" and n_players >=0:
		req = requests.post("http://"+server_ip+":5000/createGame/"+username+"/"+str(n_players))
		return "", req.status_code
	else:
		return "",400

@app.route('/joinGame/<string:username>/<int:game_id>', methods = ['PUT'])
def join_g(username,game_id):
	global joined_game_id
	req = requests.put("http://"+server_ip+":5000/joinGame/"+username+"/"+str(game_id))
	joined_game_id = game_id
	if joined_game_id == 1:
		return "bad game_id", 400
	else:
		return req.text,req.status_code
	
@app.route('/startGame', methods = ['PUT'])
def start_g():
	first_player = players.itervalues().next()
	if first_player == my_player_name:
		for p in players:
			cards = get_randomCards()
			sendCards(cards, p)

#genera le carte da gioco iniziali di un giocatore rimuovendole dal deck
def get_randomCards():
	global deck
	n = 0
	player_cards = []
	#sto usando dei magic number (20 che sarebbe la grandezza del mazzo di prova e 3 la mano dei giocatori), come si definiscono le costanti in python
	while n < 3 :
		player_cards.append( deck.pop(random.choice(range(len(deck)))) )
		n = n + 1
	return player_cards	

def sendCards(cards=None, player=None):
	if not cards or not player:
		raise ValueError("player_server: sendCards called with cards or player equal to None")
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	#crea un dizionario del deck della forma { card_id : <json dell'oggetto game_card> }
	player_cards_dict = dict((card.card_id, vars(card)) for card in cards)
	r = requests.post(url, data=json.dumps(player_cards_dict), headers=headers)
	player_url = "http://"+player.ip+":"+player.port+"/receiveCards"
	return

@app.route('/receiveCards', methods = ['POST'])
def rcvCards():
	if not request.json:
		abort(400)
	print request.json
	return jsonify(request.json)

@app.route('/table', methods = ['PUT'])
def playFirstCard():
	table.append( deck.pop(random.choice(range(len(deck)))) )
	return table

def try_ports():
	global server_port
	try:
		app.run(server_ip, server_port, threaded = True)
		return True
	except:
		server_port += 1
		print "eccezione! provo la porta: " + str(server_port)
		return False

if __name__ == "__main__":
	app.debug = True
	server_started = try_ports()
	while not server_started:
		server_started = try_ports()
	

"""	sendCards()
	print "deck dopo aver distribuito 9 carte"
	for deck_c in deck:
		print deck_c
	print "playFirstCard: "
	for c in playFirstCard():
		print "table_card: " + str(c)"""
#r = requests.get('http://localhost:5000/')
#print(r.text)

