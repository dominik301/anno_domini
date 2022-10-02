#!../framework/bin/python
import json
import random
import os
import signal
import _thread

from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit
from game_card import *
from game import *
from deck import *
from player import * #for testing
from threading import currentThread, Timer, enumerate

#lista dei giochi creati
gamesList = []

#mazzo
deck = Deck

#le carte sul tavolo
table = []

#le carte sul tavolo prima del dubbio
tablePreDoubt = []

#lista di giocatori 
players = []

#id del gioco
game_id = 0

#carte che ho in mano
hands = {}

#variabile dell'eventuale vincitore
winner = ""

#variabile per il polling del dubbio
doubtp = "";

#variabile per lo stato del dubbio 0 bene 1 male
doubtStatus = 0

#indice dei turni, mi serve per capire chi e' crashato
turn_index = 0

#variabile per stabilire il mio crash
timeOut = {}

"""game list"""
_games_ = {}

"""player list"""
_players_ = {}

"""index of games"""
index = 0

app = Flask(__name__, static_folder = "static")
io = SocketIO(app, async_mode=None)


def reset():
	global gamesList, table, tablePreDoubt, players, game_id, hands, winner, doubtp, doubtStatus, turn_index, timeOut, _games_, _players_, index
	gamesList = []
	table = []
	tablePreDoubt = []
	players = []
	game_id = 0
	hands = {}
	winner = ""
	doubtp = ""
	doubtStatus = 0
	turn_index = 0
	timeOut = {}
	_games_ = {}
	_players_ = {}
	index = 0

def _timer(plus):
	if plus:
		return Timer(70.0, time_out)
	else:
		return Timer(60.0, time_out)

def time_out():
	global turn_index
	global players
	global timeOut
	timeOut[turn_index] = True

	print("TIMEOUT: der Spieler musste diese Runde spielen:" + str(turn_index) +":"+ players[turn_index]['username'])
	players.remove(players[turn_index])
	if len(players) < 2:
		print("Zu wenige Spieler, das Spiel kann nicht weitergehen")
		reset()
		return
	if turn_index >= len(players): #Nel caso in cui ha fatto crash l'ultimo della lista
		turn_index = turn_index % len(players)
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
	return render_template("gui.html", sync_mode=io.async_mode)

#Polling dalla GUI per controllare se il timer e' esaurito
@app.route("/timeOut")
def myTimeOut():
	if turn_index in timeOut and timeOut[turn_index]:
		return jsonify({"my_timeout": True})
	else:
		return jsonify({"my_timeout": False})

#Polling dalla GUI per avere la propria mano
@io.on("mano")
def return_hand():
	_hand = []
	for i in _players_:
		if _players_[i].sid == request.sid:
			_hand = hands[i]
	emit("mano",json.dumps(_hand, default=lambda o: o.__dict__),room=request.sid,namespace='/')
	
#Polling dalla GUI per avere lo stato del gioco (in attesa o iniziato)
@app.route("/gameStatus")
def game_status():
	if len(table) == 0 :
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
		toReturn = {'status': 'doubt', 'doubter': str(doubtp), 'doubtResult': str(doubtStatus), 'table': tablePreDoubt}
		resetDoubt()
		for p in players:
			emit('bancoOrDoubt', json.dumps(toReturn, default=lambda o: o.__dict__),room=p['sid'],namespace='/')
	else: #Restituisco il banco
		jsonTurno = {'winner': winner, 'turn': 0, 'turn_index': turn_index} #TODO
		toReturn = {'status': 'normal', 'turn': jsonTurno , 'table': table}
	return json.dumps(toReturn, default=lambda o: o.__dict__)

#Metodo invocato dal browser web
@app.route('/gamesList', methods = ['GET'])
def gameList():
	games = []
	for h in gamesList:
		creator = Player(h['creator']['username'],"0.0.0.0")
		game = Game(h['game_id'],creator,h['player_n'],h['p_list'])
		games.append(game)
	return json.dumps(games, default=lambda o: o.__dict__)


@app.route('/createGame/<string:username>/<int:n_players>', methods = ['POST'])
def create_g(username, n_players):
	global index
	global _games_
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
		#informo tutti i players iscritti al server della creazione del nuovo gioco
		gamesToSend = []
		for key in _games_:
			game = Game(_games_[key].game_id, _games_[key].creator, _games_[key].player_n, [])
			gamesToSend.append(game)
		for key in _players_:
			emit('rcvGamesList',json.dumps(gamesToSend, default=lambda o: o.__dict__),room=_players_[key].sid,namespace='/')
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
			emit('startGame',json.dumps(game.p_list, default=lambda o: o.__dict__), room=i.sid,namespace='/')
	return "Game joined\n",200


#Metodo invocato dal browser web per giocare una carta
@app.route('/playCard/<int:card_id>/<int:card_pos>', methods = ['PUT'])
def playCard(card_id,card_pos):
	my_player_name = players[turn_index]['username']
	_hand = hands[my_player_name]
	for card in _hand :
		if card.card_id == card_id :
			cardToSend = card
			_hand.remove(card)
			break
	else:
		return "Karte mit unbekannter id", 400
	#Invio il messaggio della giocata a tutti gli altri giocatori
	url = "/" + my_player_name + "/" + str(cardToSend.year) + "/" + str(cardToSend.event) + "/" + str(cardToSend.card_id) + "/" + str(card_pos)
	emit('playedCard', url,room=players[turn_index]['sid'],namespace='/')
	return "ok"

started = False

#Metodo invocato dal Registrar Server
@app.route('/startGame', methods = ['PUT'])
def start_g():
	global players
	global hands
	global table
	global turn_index
	global started
	turn_index = 0
	players = request.get_json(force=True) #Restituisce lista di dizionari: ogni dizionario corrisponde a un player
	if started:
		return "", 200
	started = True
	table.append(deck.pop(random.choice(list(range(len(deck))))))
	for p in players:
		cards = get_randomCards()
		hands[p['username']] = cards

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
	print("Ich erhalte eine Liste von Spielen")
	global gamesList
	gamesList = request.get_json(force=True)
	return "",200

#Metodo invocato da un altro player_server
#L'username serve perche' nel test in localhost l'ip e' sempre lo stesso e non si riesce a riconoscere gli utenti
@app.route('/playedCard/<string:username>/<int:year>/<string:event>/<int:card_id>/<int:position>', methods = ['PUT'])
def playedCard(username, year, event, card_id, position):
	print("Karte gespielt von", username)
	#la prima cosa che faccio e' resettare il timer del timeout
	global turn_index
	global winner
	reset_timer(False)
	cardToInsert = Game_Card(year, event, card_id)
	table.insert(position, cardToInsert)
	if players[turn_index]['username'] == username:
		players[turn_index]['n_cards'] = str(int(players[turn_index]['n_cards']) - 1)
		if players[turn_index]['n_cards'] == "0": #Auto-dubito (ATTENZIONE: avviene localmente in tutti i nodi senza scambio di msg)
			winner_index = turn_index
			turn_index = ((turn_index + 1) % len(players))
			returned = doubt()
			if returned[0]=="End":
				winner = players[winner_index]['username']
				print("\nIl gioco e' finito! Il vincitore e' " + winner + "\n")
				reset()
				return "", 200
		else:
			turn_index = ((turn_index + 1) % len(players))
	#il giocatore da cui mi aspettavo la giocata e' crashato: mi e' arrivata la giocata da quello successivo
	elif players[(turn_index+1) % len(players)]['username'] == username:
		print("Es spielte der nächste Spieler, anders als ich erwartet hatte")
		print("Elimino ", players[turn_index]['username'], " (",turn_index,")")
		players.remove(players[turn_index])
		if turn_index >= len(players): #Nel caso in cui ha fatto crash l'ultimo della lista
			turn_index = turn_index % len(players)
		turn_index = ((turn_index + 1) % len(players))
	else:
		return "Unexcepted player", 400
	print("Jetzt ist an der Reihe: " + players[turn_index]['username'])
	return "", 200

#Metodo che fa il pop di n carte dal mazzo e le restituisce come lista
def pesca(n):
	pescate = []
	for i in range(0,n):
		pescate.append(deck.pop(0))
	return pescate

#Metodo invocato dal nodo che dubita
@app.route('/doubt', methods = ['PUT'])
def doubt(): #il param. e' l'username di chi invia il messaggio
	reset_timer(True)
	global table
	global tablePreDoubt
	global turn_index
	global doubtp
	global doubtStatus
	if len(table) < 2:
		return "", 400
	doubtp = players[turn_index]['username']
	tablePreDoubt = table
	doubterIndex = turn_index
	print("Doubter = ", doubterIndex, players[doubterIndex])
	
	prevIndex = doubterIndex - 1
	if prevIndex == -1:
		prevIndex = len(players) - 1
	
	for i in range(0, len(table) - 1):
		if table[i].year > table[i+1].year:
			#Il dubbio era fondato: si penalizza il precedente nella mano
			print("\n", players[turn_index]['username'], "hat richtig gezweifelt")
			doubtStatus = 0;
			penalizatedIndex = prevIndex
			penalization = 3
			nextPlayerIndex = doubterIndex
			break
	else:
		#Dubitato male
		print("\n", players[turn_index]['username'], "hat zu Unrecht gezweifelt")
		doubtStatus = 1;
		#Puo' essere che il gioco sia finito (siamo in auto-dubito e l'ultimo player ha 0 carte)
		if int(players[prevIndex]['n_cards']) == 0:
			return "End", 200
		#Gioco non finito: colui che ha dubitato deve essere penalizzato
		penalizatedIndex = doubterIndex
		penalization = 2
		nextPlayerIndex = (doubterIndex + 1) % len(players)
	pescate = pesca(penalization)
	_hand = hands[players[penalizatedIndex]['username']]
	for c in pescate:
		_hand.append(c)
	print("Spieler hat " + str(penalization) + " Karten gezogen")
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
	print("Jetzt ist an der Reihe: " + players[turn_index]['username'])
	return "",200

def resetDoubt():
	global doubtp
	if doubtp != "":
		doubtp = ""

#only for testing
@app.route("/playerList", methods = ['GET'])
def get_players():
	players_dict = dict((_players_.get(player).username, _players_.get(player).sid) for player in _players_)
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
	print(game_list)
	return json.dumps(game_list, default=lambda o: o.__dict__)

#only for testing
@app.route("/printGames", methods = ['GET'])
def print_games():
	for item in _games_:
		print(_games_[item])
	return "",200

@io.on('createPlayer')
def create_p(username):
	new_p = Player(username, request.sid)
	if new_p.username not in _players_:
		for p in _players_:
			if _players_[p].sid == new_p.sid:
				emit('createErr',"You have already been registered\n", room=new_p.sid)
				return "You have already been registered\n", 400
		_players_[new_p.username] = new_p
		if len(_games_) != 0: #invio l'elenco dei giochi al nuovo iscritto
			gamesToSend = []
			for key in _games_:
				game = Game(_games_[key].game_id, _games_[key].creator, _games_[key].player_n, [])
				gamesToSend.append(game)
			emit('rcvGamesList',json.dumps(gamesToSend, default=lambda o: o.__dict__), room=new_p.sid,namespace='/')
	else:
		emit('createErr',"Username already chosen\n", room=new_p.sid,namespace='/')
		return "Username already chosen\n", 400
	emit('createSuccess',"Registriert\n", room=new_p.sid,namespace='/')
	return "Registrato", 201

if __name__ == "__main__":
	_thread.start_new_thread(lambda: io.run(app, debug=False), ())

	for t in enumerate():
		if currentThread() != t and t.__class__.__name__ != "_DummyThread" and t.__class__.__name__ != "_MainThread":
			print("try joining: " + str(t))
			#t.join()
			if t.__class__.__name__ == "_Timer":
				t.cancel()
				print("timeout canceled!")
