#!../framework/bin/python
import requests
import json
import random
from flask import Flask, jsonify, request, abort
from game_card import *

#mazzo
deck = []
for j in range(0,20):
	deck.append( Game_Card(j, "e_" + str(j), j) )
#le carte sul tavolo
table = []

#lista di giocatori per il testing
players = ["stefano","vincenzo","roberto"]

app = Flask(__name__)
server_ip = "0.0.0.0"
server_port = 5000

@app.route("/")
def hello():
	return "sono il server_player_0\n"


@app.route('/createPlayer/<string:username>', methods = ['POST'])
def create_p(username):
	if username != "":
		req = requests.post("http://"+server_ip+":"+server_port+"/createPlayer/"+username)
		return req.status_code
	else:
		return "",400

@app.route('/createGame/<string:username>/<int:n_players>', methods = ['POST'])
def create_g(username, n_players):
	if username != "" and n_players >=0:
		req = requests.post("http://"+server_ip+":"+server_port+"/createGame/"+username+"/"+str(n_players))
		return req.status_code
	else:
		return "",400

@app.route('/joinGame/<string:username>/<int:game_id>', methods = ['PUT'])
def join_g(username,game_id):
	return requests.put("http://localhost:5000/joinGame/username/game_id")

#invia una lista di carte ad un giocatore, per ora ci sono solo stampe di debug
def send_c(cards, player):
	print player + " received:\n",
	for c in cards:
		print c

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

@app.route('/cards', methods = ['PUT'])
def sendCards():
	#lista di giocatori per il testing
	#players = ["stefano","vincenzo","roberto"]
	#and len( deck ) >= (20 - the_game.player_n * 3)
	#for p in players:
	#	send_c(get_randomCards(), p)

	#crea un dizionario del deck della forma { card_id : <json dell'oggetto game_card> }
	deck_dict = dict((card.card_id, vars(card)) for card in deck)
	#test di invio delle carte di un giocatore generate in modo random e rimosse dal deck
	player_cards_dict = dict((card.card_id, vars(card)) for card in get_randomCards())
	url = "http://localhost:5001/receiveCards"
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	r = requests.post(url, data=json.dumps(player_cards_dict), headers=headers)
	return jsonify(player_cards_dict)

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
		app.run(server_ip, server_port)
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

