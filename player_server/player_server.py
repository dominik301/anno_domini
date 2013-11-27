#!../framework/bin/python
import requests
import json
import random
from flask import Flask, jsonify, request, abort
from game_card import *
from deck import *
from player import * #for testing
#mazzo
deck = Deck

#il mio nome
my_player_name = ""

#le carte sul tavolo
table = []

#lista di giocatori 
players = []
#carte che ho in mano
hand = []

app = Flask(__name__)
server_ip = "127.0.0.1"
server_port = 5000

@app.route("/")
def hello():
	return "sono il server_player ip: " + server_ip + " porta: " + str(server_port) + "\n"


@app.route('/createPlayer/<string:username>', methods = ['POST'])
def create_p(username):
	global my_player_name
	if username != "":
		porta = request.host[request.host.find(':') + 1 :]
		req = requests.post("http://"+server_ip+":5000/createPlayer/"+username+"/"+porta)
		my_player_name = username
		return "", req.status_code
	else:
		return "",400

#Eliminare parametro username??
@app.route('/createGame/<int:n_players>', methods = ['POST'])
def create_g(n_players):
	if my_player_name != "" and n_players >=0:
		req = requests.post("http://"+server_ip+":5000/createGame/"+my_player_name+"/"+str(n_players))
		return "", req.status_code
	else:
		return "",400

#Eliminare parametro username??
@app.route('/joinGame/<int:game_id>', methods = ['PUT'])
def join_g(game_id):
	req = requests.put("http://"+server_ip+":5000/joinGame/"+my_player_name+"/"+str(game_id))
	return req.text,req.status_code
	
@app.route('/startGame', methods = ['PUT'])
def start_g():
	global players
	global hand
	global table
	players = request.json #Restituisce lista di dizionari: ogni dizionario corrisponde a un player
	if players[0]['username'] == my_player_name:
		hand = get_randomCards()
		table.append(deck.pop(0))
		for p in players:
			if p['username'] != my_player_name:
				print "invio a: "+ p['username']+ " le carte "
				cards = get_randomCards()
				headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

				#invio le carte da gioco ai giocatori
				url = "http://"+p['ip']+":"+str(p['porta'])+"/receiveCards"
				r = requests.post(url, json.dumps(cards, default=lambda o: o.__dict__), headers=headers)

				#invio il tavolo da gioco ai giocatori
				url = "http://"+p['ip']+":"+str(p['porta'])+"/receiveTable"
				s = requests.post(url, json.dumps(table, default=lambda o: o.__dict__), headers=headers)

				#invio il mazzo ai giocatori
				url = "http://"+p['ip']+":"+str(p['porta'])+"/receiveDeck"
				s = requests.post(url, json.dumps(deck, default=lambda o: o.__dict__), headers=headers)
	print "la mia mano"
	for m in hand:
		print m
	print "il tabolo"
	print table
	return "", 200

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

@app.route('/receiveCards', methods = ['POST'])
def rcvCards():
	print "Ricevo carte"
	if not request.json:
		abort(400)
	hand_json = request.json
	for h in hand_json:
		card = Game_Card(h['year'],h['event'],h['card_id'])
		hand.append(card)
	for c in hand:
		print c
	return "",200

@app.route('/receiveTable', methods = ['POST'])
def rcvTable():
	print "Ricevo tavolo"
	if not request.json:
		abort(400)
	table_json = request.json
	for t in table_json:
		card = Game_Card(t['year'],t['event'],t['card_id'])
		table.append(card)
	for c in table:
		print c
	return "",200

@app.route('/receiveDeck', methods = ['POST'])
def rcvDeck():
	global deck
	print "Ricevo deck"
	if not request.json:
		abort(400)
	deck_json = request.json
	tmp_deck = []
	for d_card in deck_json:
		card = Game_Card(d_card['year'],d_card['event'],d_card['card_id'])
		tmp_deck.append(card)
	deck = tmp_deck
	for c in deck:
		print c
	return "",200

@app.route('/initTable', methods = ['PUT'])
def playFirstCard():
	table.append( deck.pop(random.choice(range(len(deck)))) )
	return table

#metodo richiamato dal browser per giocare una carta
@app.route('/playCard/<int:card_id>/<int:card_pos>', methods = ['PUT'])
def playCard(card_id,card_pos):
	print "mano prima della giocata"
	for x in hand :
		print x
	for card in hand :
		if card.card_id == card_id :
			cardToSend = card
			hand.remove(card)
	print "mano dopo la giocata"
	for x in hand :
		print x
	for users in players:
		url = "http://"+users['ip']+":"+str(users['porta'])+"/playedCard"
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		r = requests.put(url, data=json.dumps({"year":cardToSend.year,"event":cardToSend.event,"card_id":cardToSend.card_id,"card_pos":card_pos}), headers=headers)
	return "ok"

@app.route('/playedCard',methods = ['PUT'])
def playedCard():
	print "banco prima della carta giocata"
	for i in table:	#only for test
		print i 	#
	card = request.json
	print card['event'] #only for test
	cardtoInsert = Game_Card(card['year'],card['event'],card['card_id'])
	table.insert(card['card_pos'],cardtoInsert)
	print "banco dopo la carta giocata"
	for i in table:	#only for test
		print i 	#
	return "ok"

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

