#!../framework/bin/python
import sys
import requests
import json
import random
import sys
import os
import signal

from flask import Flask, jsonify, request, abort, render_template
from game_card import *
from game import *
from deck import *
from player import * #for testing
from datetime import timedelta
from flask import make_response,current_app
from functools import update_wrapper
from threading import *

#lista dei giochi creati
gamesList = []

#mazzo
deck = Deck

#il mio nome
my_player_name = ""

#le carte sul tavolo
table = []

#le carte sul tavolo prima del dubbio
tablePreDoubt = []

#lista di giocatori 
players = []

#id del gioco
game_id = 0

#carte che ho in mano
hand = []

#variabile per il polling del turno
my_turn = False;

#variabile dell'eventuale vincitore
winner = ""

#variabile per il polling del dubbio
doubtp = "";

#variabile per lo stato del dubbio 0 bene 1 male
doubtStatus = 0

#indice dei turni, mi serve per capire chi e' crashato
turn_index = 0

#variabile per stabilire il mio crash
my_timeout = False

app = Flask(__name__, static_folder = "static")
server_ip = "127.0.0.1"
server_port = 5000
my_ip = "0.0.0.0"
my_port = 5001


def _timer(plus):
	if plus:
		return Timer(70.0, time_out)
	else:
		return Timer(60.0, time_out)

def time_out():
	global turn_index
	global my_turn
	global players
	global my_timeout

	#per avvisare il browser che sono io che ho fatto crash	
	if my_turn == True:
		my_turn = False
		my_timeout = True

	print("TIMEOUT: doveva giocare il giocatore del turno:" + str(turn_index) +":"+ players[turn_index]['username'])
	players.remove(players[turn_index])
	if len(players) < 4:
		print("Troppi pochi giocatori la partita non puo' andare avanti")
		return
	if turn_index >= len(players): #Nel caso in cui ha fatto crash l'ultimo della lista
		turn_index = turn_index % len(players)
	if players[turn_index]['username'] == my_player_name and my_turn == False:
		my_turn = True
	reset_timer(False)

#timer (corrente: viene di volta in volta rinnovato con i reset) di ogni giocatore
player_timer = _timer(False)

def reset_timer(plus):
	global player_timer
	player_timer.cancel()
	player_timer = _timer(plus)
	player_timer.start()

def terminate_app():
	#qui eseguo la kill sul gruppo di processi attivi per questo player_server
	pid_g = os.getpgrp()
	os.killpg(pid_g, signal.SIGKILL)

@app.route("/")
def hello():
	print("Sono il server_player: IP: " + my_ip + " porta: " + str(my_port) + "\n", 200)
	return render_template("gui.html")

#Polling dalla GUI per controllare se il timer e' esaurito
@app.route("/timeOut")
def myTimeOut():
	return jsonify({"my_timeout": my_timeout})

#Polling dalla GUI per avere la propria mano
@app.route("/mano")
def return_hand():
	return json.dumps(hand, default=lambda o: o.__dict__)
	
#Polling dalla GUI per avere lo stato del gioco (in attesa o iniziato)
@app.route("/gameStatus")
def game_status():
	if len(hand) == 0 or len(table) == 0 :
		return jsonify({'status' : 0})
	return jsonify({'status' : 1})

#Polling dalla GUI per avere il numero delle carte degli altri
@app.route("/playerCards")
def playerCards():
	cards_dict = {}
	i = 0
	for p in players:
		cards_dict[i] = {'username': p['username'], 'n_cards' : p['n_cards']}
		i = i+1
	return jsonify(cards_dict)

#Polling dalla GUI per avere lo stato del gioco dopo l'inizio	
@app.route("/bancoOrDoubt", methods=['GET'])
def bancoOrDoubt():
	if doubtp != "": #Restituisco lo stato del dubito
		temp = doubtp
		toReturn = {'status': 'doubt', 'doubter': str(doubtp), 'doubtResult': str(doubtStatus), 'table': tablePreDoubt}
		resetDoubt()
	else: #Restituisco il banco
		if my_turn:
			turno = 1
		else:
			turno = 0
		jsonTurno = {'winner': winner, 'turn': turno, 'turn_index': turn_index}
		toReturn = {'status': 'normal', 'turn': jsonTurno , 'table': table}
	return json.dumps(toReturn, default=lambda o: o.__dict__)

#Metodo invocato dal browser web
@app.route('/createPlayer/<string:username>', methods = ['POST'])
def create_p(username):
	global my_player_name
	if username != "":
		req = requests.post("http://"+server_ip+":"+str(server_port)+"/createPlayer/"+username+"/"+str(my_port))
		my_player_name = username
		return req.text, req.status_code
	else:
		return "Username cannot be empty",400

#Metodo invocato dal browser web
@app.route('/gamesList', methods = ['GET'])
def gameList():
	games = []
	for h in gamesList:
		creator = Player(h['creator']['username'],"0.0.0.0")
		game = Game(h['game_id'],creator,h['player_n'],h['p_list'])
		games.append(game)
	return json.dumps(games, default=lambda o: o.__dict__)
	
#Metodo invocato dal browser web
@app.route('/createGame/<int:n_players>', methods = ['POST'])
def create_g(n_players):
	if my_player_name != "" and n_players >=1:
		req = requests.post("http://"+server_ip+":"+str(server_port)+"/createGame/"+my_player_name+"/"+str(n_players))
		global game_id
		if req.status_code == 400:
			return req.text, req.status_code
		game_id = int(req.text)
		return req.text, req.status_code
	else:
		return "Username cannot be empty and number of players cannot be less than 1",400

#Metodo invocato dal browser web
@app.route('/joinGame/<int:id_game>', methods = ['PUT'])
def join_g(id_game):
	req = requests.put("http://"+server_ip+":"+str(server_port)+"/joinGame/"+my_player_name+"/"+str(id_game))
	global game_id
	game_id = id_game
	return req.text, req.status_code

#Metodo invocato dal browser web per giocare una carta
@app.route('/playCard/<int:card_id>/<int:card_pos>', methods = ['PUT'])
def playCard(card_id,card_pos):
	global my_turn
	for card in hand :
		if card.card_id == card_id :
			cardToSend = card
			hand.remove(card)
			break
	else:
		return "Carta con id sconosciuto", 400
	#Invio il messaggio della giocata a tutti gli altri giocatori
	my_turn = False
	for user in players:
		url = "http://"+user['ip']+":"+str(user['porta'])+"/playedCard"
		url = url + "/" + my_player_name + "/" + str(cardToSend.year) + "/" + str(cardToSend.event) + "/" + str(cardToSend.card_id) + "/" + str(card_pos)
		r = requests.put(url) #TODO: da' sempre "ok" come esito?! vedere se una delle put da errore e restituire 400
	return "ok"


#Metodo invocato dal browser web per dubitare
@app.route('/doubt', methods = ['PUT'])
def doubt():
	global my_turn
	if len(table) < 2:
		return "", 400
	my_turn = False
	for x in players: #lo invia anche a se' stesso
			url = "http://" + x['ip'] + ":" + str(x['porta']) + "/doubted/" + my_player_name
			r = requests.put(url)
	return r.text, 200




#Metodo invocato dal Registrar Server
@app.route('/startGame', methods = ['PUT'])
def start_g():
	global players
	global hand
	global table
	global my_turn
	global turn_index
	turn_index = 0
	players = request.json #Restituisce lista di dizionari: ogni dizionario corrisponde a un player
	if players[0]['username'] == my_player_name:
		my_turn = True
		hand = get_randomCards()
		table.append(deck.pop(random.choice(list(range(len(deck))))))
		for p in players:
			if p['username'] != my_player_name:

				cards = get_randomCards()
				headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

				#invio le carte da gioco ai giocatori
				url = "http://"+p['ip']+":"+str(p['porta'])+"/receiveCards"
				r = requests.post(url, json.dumps(cards, default=lambda o: o.__dict__), headers=headers)

				#invio il tavolo da gioco ai giocatori
				url = "http://"+p['ip']+":"+str(p['porta'])+"/receiveTable"
				s = requests.post(url, json.dumps(table, default=lambda o: o.__dict__), headers=headers)

		#invio il mazzo ai giocatori
		for p in players:
			if p['username'] != my_player_name:
				url = "http://"+p['ip']+":"+str(p['porta'])+"/receiveDeck"
				t = requests.post(url, json.dumps(deck, default=lambda o: o.__dict__), headers=headers)
		#Richiamare la funzione della GUI per la prima giocata

	player_timer.start()
	return "", 200

#Genera le carte da gioco iniziali di un giocatore rimuovendole dal deck
def get_randomCards():
	global deck
	player_cards = []
	#sto usando dei magic number (20 che sarebbe la grandezza del mazzo di prova e 3 la mano dei giocatori), come si definiscono le costanti in python
	for n in range (0,7) :
		player_cards.append( deck.pop(random.choice(list(range(len(deck))))) )
	return player_cards	

#Metodo invocato dal Registrar Server per inviare l'elenco delle partite
@app.route("/rcvGamesList", methods = ['POST'])
def rcvGamesList():
	print("Ricevo elenco games")
	global gamesList
	gamesList = request.json
	return "",200

#Metodo invocato dal player_server creator per inviare le carte di mano
@app.route('/receiveCards', methods = ['POST'])
def rcvCards():
	print("Ricevo carte")
	if not request.json:
		return "There is no data in http header", 400
	hand_json = request.json
	for h in hand_json:
		card = Game_Card(h['year'],h['event'],h['card_id'])
		hand.append(card)
	return "", 200 

#Metodo invocato dal player_server creator per inviare il banco iniziale
@app.route('/receiveTable', methods = ['POST'])
def rcvTable():
	print("Ricevo tavolo")
	if not request.json:
		return "There is no data in http header", 400
	table_json = request.json
	for t in table_json:
		card = Game_Card(t['year'],t['event'],t['card_id'])
		table.append(card)
	return "",200

#Metodo invocato dal player_server creator per inviare il deck
@app.route('/receiveDeck', methods = ['POST'])
def rcvDeck():
	global deck
	print("Ricevo deck")
	if not request.json:
		return "There is no data in http header", 400
	deck_json = request.json
	tmp_deck = []
	for d_card in deck_json:
		card = Game_Card(d_card['year'],d_card['event'],d_card['card_id'])
		tmp_deck.append(card)
	deck = tmp_deck
	return "",200

#Metodo invocato da un altro player_server
#L'username serve perche' nel test in localhost l'ip e' sempre lo stesso e non si riesce a riconoscere gli utenti
@app.route('/playedCard/<string:username>/<int:year>/<string:event>/<int:card_id>/<int:position>', methods = ['PUT'])
def playedCard(username, year, event, card_id, position):
	print("Carta giocata da", username)
	#la prima cosa che faccio e' resettare il timer del timeout
	global turn_index
	global my_turn
	global winner
	reset_timer(False)
	cardToInsert = Game_Card(year, event, card_id)
	table.insert(position, cardToInsert)
	if players[turn_index]['username'] == username:
		players[turn_index]['n_cards'] = str(int(players[turn_index]['n_cards']) - 1)
		if players[turn_index]['n_cards'] == "0": #Auto-dubito (ATTENZIONE: avviene localmente in tutti i nodi senza scambio di msg)
			winner_index = turn_index
			turn_index = ((turn_index + 1) % len(players))
			returned = doubted(players[turn_index]['username'])
			if returned[0]=="End":
				winner = players[winner_index]['username']
				print("\nIl gioco e' finito! Il vincitore e' " + winner + "\n")
				return "", 200
		else:
			turn_index = ((turn_index + 1) % len(players))
	#il giocatore da cui mi aspettavo la giocata e' crashato: mi e' arrivata la giocata da quello successivo
	elif players[(turn_index+1) % len(players)]['username'] == username:
		print("Ha giocato il successivo a quello che aspettavo")
		print("Elimino ", players[turn_index]['username'], " (",turn_index,")")
		players.remove(players[turn_index])
		if turn_index >= len(players): #Nel caso in cui ha fatto crash l'ultimo della lista
			turn_index = turn_index % len(players)
		turn_index = ((turn_index + 1) % len(players))
	else:
		return "Unexcepted player", 400
	if players[turn_index]['username'] == my_player_name:
		my_turn = True
	print("Adesso e' il turno di: " + players[turn_index]['username'])
	return "", 200

#Metodo che fa il pop di n carte dal mazzo e le restituisce come lista
def pesca(n):
	pescate = []
	for i in range(0,n):
		pescate.append(deck.pop(0))
	return pescate

#Metodo invocato dal nodo che dubita
@app.route('/doubted/<string:username>', methods = ['PUT'])
def doubted(username): #il param. e' l'username di chi invia il messaggio
	reset_timer(True)
	global table
	global tablePreDoubt
	global my_turn
	global turn_index
	global doubtp
	global doubtStatus
	doubtp = username
	tablePreDoubt = table
	#E' arrivata la giocata dal successivo a quello da cui me l'aspettavo
	if players[(turn_index+1)%len(players)]['username'] == username:
		players.remove(players[turn_index])
		if turn_index >= len(players):
			turn_index = turn_index % len(players)
	elif players[turn_index]['username'] != username:
		return "Unexpected player", 400
	doubterIndex = turn_index
	print("Doubter = ", doubterIndex, players[doubterIndex])
	
	myIndex = -1
	for user in players:
		if user['username'] == my_player_name:
			myIndex = players.index(user)
		if myIndex > -1:# and doubterIndex > -1: #inutile continuare a cercare
			break
	prevIndex = doubterIndex - 1
	if prevIndex == -1:
		prevIndex = len(players) - 1
	
	for i in range(0, len(table) - 1):
		if table[i].year > table[i+1].year:
			#Il dubbio era fondato: si penalizza il precedente nella mano
			print("\n", players[turn_index]['username'], "ha dubitato bene")
			doubtStatus = 0;
			penalizatedIndex = prevIndex
			penalization = 3
			nextPlayerIndex = doubterIndex
			break
	else:
		#Dubitato male
		print("\n", players[turn_index]['username'], "ha dubitato male")
		doubtStatus = 1;
		#Puo' essere che il gioco sia finito (siamo in auto-dubito e l'ultimo player ha 0 carte)
		if int(players[prevIndex]['n_cards']) == 0:
			return "End", 200
		#Gioco non finito: colui che ha dubitato deve essere penalizzato
		penalizatedIndex = doubterIndex
		penalization = 2
		nextPlayerIndex = (doubterIndex + 1) % len(players)
	pescate = pesca(penalization)
	if penalizatedIndex == myIndex:  #il penalizzato inserisce le carte nella mano
		for c in pescate:
			hand.append(c)
		print("Ho pescato " + str(penalization) + " carte: la mia mano")
	#Tutti i giocatori aggiornano il counter delle carte del penalizzato
	players[penalizatedIndex]['n_cards'] = str(int(players[penalizatedIndex]['n_cards']) + penalization)
	#In ogni caso (sia dubitato bene, sia male) resetto il tavolo
	#e inserisco le carte rimaste alla fine del mazzo
	for c in table:
		deck.append(c)
	table = []
	table.append(deck.pop(0))
	#Verifico se e' il mio turno
	turn_index = nextPlayerIndex
	if myIndex == turn_index:
		my_turn = True
	print("Adesso e' il turno di: " + players[turn_index]['username'])
	return "",200

def resetDoubt():
	global doubtp
	if doubtp != "":
		doubtp = ""



def try_ports():
	global my_port
	try:
		app.run(my_ip, my_port, threaded = True)
		return True
	except:
		my_port += 1
		print("Eccezione! Provo la porta: " + str(my_port))
		return False

if __name__ == "__main__":
	if len(sys.argv) == 1:
		my_ip = "127.0.0.1"
		server_ip = "127.0.0.1"
	elif len(sys.argv) == 3:
		my_ip = sys.argv[1]
		server_ip = sys.argv[2]
	else:
		print("Usage:", sys.argv[0], "<public IP><server IP>")
		exit(1)
	app.debug = True
	server_started = try_ports()
	while not server_started:
		server_started = try_ports()

	for t in enumerate():
		if currentThread() != t and t.__class__.__name__ != "_DummyThread" and t.__class__.__name__ != "_MainThread":
			print("try joining: " + str(t))
			#t.join()
			if t.__class__.__name__ == "_Timer":
				t.cancel()
				print("timeout canceled!")

	sys.exit()
