#!../framework/bin/python
import sys
import requests
import json
import random
import sys

from flask import Flask, jsonify, request, abort, render_template
from game_card import *
from game import *
from deck import *
from player import * #for testing
from datetime import timedelta
from flask import make_response,current_app
from functools import update_wrapper
from threading import *

#mazzo
deck = Deck

#il mio nome
my_player_name = ""

#le carte sul tavolo
table = []

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



def _timer():
	return Timer(6000.0, time_out)

def reset_timer():
	global player_timer
	print "resetto il timer"
	player_timer.cancel()
	player_timer = _timer()
	player_timer.start()

def time_out():
	global turn_index
	global my_turn
	global players
	global my_timeout

	#per avvisare il browser che sono io che ho fatto crash	
	if my_turn == True:
		print("e il mio crash")
		my_turn = False
		my_timeout = True
	print "TIMEOUT: doveva giocare il giocatore del turno:" + str(turn_index) +":"+ players[turn_index]['username']
	players.remove(players[turn_index])
	print "giocatori rimasti: " + str(len(players))
	if len(players) < 4:
		print "troppi pochi giocatori la partita non puo' andare avanti"
		return
	if turn_index >= len(players): #Nel caso in cui ha fatto crash l'ultimo della lista
		turn_index = turn_index % len(players)
	if players[turn_index]['username'] == my_player_name and my_turn == False:
		print "OO GUARDA CASO TORNA A ME"
		my_turn = True
	print "Time out...ora deve giocare il giocatore di indice: " + players[turn_index]['username']
	reset_timer()


#timer (corrente: viene di volta in volta rinnovato con i reset) di ogni giocatore
player_timer = _timer()

@app.route("/playersLeft")
def playerLeft():
	return str(len(players))

@app.route("/timeOut")
def myTimeOut():
	return jsonify({"my_timeout": my_timeout})

@app.route("/")
def hello():
	print "Sono il server_player: IP: " + my_ip + " porta: " + str(my_port) + "\n", 200
	return render_template("prova.html")

@app.route("/banco")
def return_table():
	return json.dumps(table, default=lambda o: o.__dict__)

@app.route("/mano")
def return_hand():
	return json.dumps(hand, default=lambda o: o.__dict__)
	
#metodo per il polling
@app.route("/gameStatus")
def game_status():
	if len(hand) == 0 and len(table) == 0 :
		return jsonify({'status' : 0})
	return jsonify({'status' : 1})

#servizio per ottenere il numero di carte degli altri giocatori
@app.route("/playerCards")
def playerCards():
	cards_dict = {}
	for p in players:
		cards_dict[p['username']] = p['n_cards']
	return jsonify(cards_dict)

@app.route("/turnStatus")
def turn_status():
	if my_turn:
		toreturn = 1
	else:
		toreturn = 0
	return jsonify({'winner' : winner, 'turn' : toreturn})

@app.route("/doubtStatus")
def doubt_status():
	if doubtp == "" :
		return jsonify({'doubt' : 0})
	temp = doubtp
	resetDoubt()
	return jsonify({'doubt' : str(temp),'status': str(doubtStatus)})
	
#Metodo invocato dal browser web
@app.route('/createPlayer/<string:username>', methods = ['POST'])
def create_p(username):
	global my_player_name
	if username != "":
		req = requests.post("http://"+server_ip+":"+str(server_port)+"/createPlayer/"+username+"/"+str(my_port))
		print "http://"+server_ip+":"+str(server_port)+"/createPlayer/"+username+"/"+str(my_port)
		my_player_name = username
		return req.text, req.status_code
	else:
		return "Username cannot be empty",400

@app.route('/gamesList', methods = ['GET'])
def gameList():
	games = []
	req = requests.get("http://"+server_ip+":5000/gameList")
	#se ritorna una lista vuota....
	if req.text == "[]" :
		return jsonify({'zero': 0})
		return "There is no data in http header", 400
	games_json = req.json()
	print req.json()
	for h in games_json:
		print "IL CREATORE E "+h['creator']['username']
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

#Metodo invocato dal browser web
@app.route('/unsubscribe', methods = ['DELETE'])
def unsubscribe():
	if len(players) == 0:
		req = requests.delete("http://"+server_ip+":"+str(server_port)+"/unsubscribe/"+my_player_name+"/"+str(game_id))
		return req.text, req.status_code

#Metodo invocato dal registrar server
@app.route('/startGame', methods = ['PUT'])
def start_g():
	print("SONO NELLA START GAME");
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
		table.append(deck.pop(random.choice(range(len(deck)))))
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

	print "\nLa mia mano"
	for m in hand:
		print "ID="+str(m.card_id)+" Y="+str(m.year)
	print "\nIl tavolo"
	for x in table:
		print "ID="+str(x.card_id)+" Y="+str(x.year)

	player_timer.start()

	return "", 200


#genera le carte da gioco iniziali di un giocatore rimuovendole dal deck
def get_randomCards():
	global deck
	player_cards = []
	#sto usando dei magic number (20 che sarebbe la grandezza del mazzo di prova e 3 la mano dei giocatori), come si definiscono le costanti in python
	for n in range (0,7) :
		player_cards.append( deck.pop(random.choice(range(len(deck)))) )
	return player_cards	

#Metodo invocato dal player_server creator
@app.route('/receiveCards', methods = ['POST'])
def rcvCards():
	print "Ricevo carte"
	if not request.json:
		return "There is no data in http header", 400
	hand_json = request.json
	for h in hand_json:
		card = Game_Card(h['year'],h['event'],h['card_id'])
		hand.append(card)
	for c in hand:
		print "ID="+str(c.card_id)+" Y="+str(c.year)
	return "", 200 

#Metodo invocato dal player_server creator
@app.route('/receiveTable', methods = ['POST'])
def rcvTable():
	print "Ricevo tavolo"
	if not request.json:
		return "There is no data in http header", 400
	table_json = request.json
	for t in table_json:
		card = Game_Card(t['year'],t['event'],t['card_id'])
		table.append(card)
	for c in table:
		print "ID="+str(c.card_id)+" Y="+str(c.year)
	return "",200

#Metodo invocato dal player_server creator
@app.route('/receiveDeck', methods = ['POST'])
def rcvDeck():
	global deck
	print "Ricevo deck"
	if not request.json:
		return "There is no data in http header", 400
	deck_json = request.json
	tmp_deck = []
	for d_card in deck_json:
		card = Game_Card(d_card['year'],d_card['event'],d_card['card_id'])
		tmp_deck.append(card)
	deck = tmp_deck
	print "Il mazzo ha", str(len(deck)), "carte"
	return "",200

#Metodo richiamato dal browser per giocare una carta
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
	print "\nMano dopo la giocata (",len(hand),")"
	for x in hand :
		print "ID="+str(x.card_id)+" Y="+str(x.year)
	#Invio il messaggio della giocata a tutti gli altri giocatori
	my_turn = False
	for user in players:
		url = "http://"+user['ip']+":"+str(user['porta'])+"/playedCard"
		url = url + "/" + my_player_name + "/" + str(cardToSend.year) + "/" + str(cardToSend.event) + "/" + str(cardToSend.card_id) + "/" + str(card_pos)
		r = requests.put(url) #TODO: da' sempre "ok" come esito?! vedere se una delle put da errore e restituire 400
	return "ok"

#Funzione per testare il fatto che il giocatore successivo a quello da cui ci si aspetta
#la giocata rileva per prima il crash. Quindi biogna far seguire da terminale il 
#comando playCard o doubt per simulare la giocata prima che gli altri possano
#accorgersi del crash.
#@app.route('/morto', methods=['GET'])
#def morto():
#	time_out()
#	return "", 200

#Metodo invocato da un altro player_server
#L'username serve perche' nel test in localhost l'ip e' sempre lo stesso e non si riesce a riconoscere gli utenti
@app.route('/playedCard/<string:username>/<int:year>/<string:event>/<int:card_id>/<int:position>', methods = ['PUT'])
def playedCard(username, year, event, card_id, position):
	#la prima cosa che faccio e' resettare il timer del timeout
	global turn_index
	global my_turn
	global winner
	reset_timer()
	cardToInsert = Game_Card(year, event, card_id)
	table.insert(position, cardToInsert)
	print "\nBanco dopo la carta giocata"
	for i in table:	#only for test
		print "ID="+str(i.card_id)+" Y="+str(i.year)
	if players[turn_index]['username'] == username:
		print "ha giocato chi mi aspettavo"
		players[turn_index]['n_cards'] = str(int(players[turn_index]['n_cards']) - 1)
		if players[turn_index]['n_cards'] == "0": #Auto-dubito (ATTENZIONE: avviene localmente in tutti i nodi senza scambio di msg)
			winner_index = turn_index
			turn_index = ((turn_index + 1) % len(players))
			returned = doubted(players[turn_index]['username'])
			if returned[0]=="End":
				winner = players[winner_index]['username']
				print "\n IL GIOCO E' FINITO! IL VINCITORE E' " + winner + "\n"
				return "", 200
		else:
			turn_index = ((turn_index + 1) % len(players))
	#il giocatore da cui mi aspettavo la giocata e' crashato: mi e' arrivata la giocata da quello successivo
	elif players[(turn_index+1) % len(players)]['username'] == username:
		print "Ha giocato il successivo a quello che aspettavo"
		print "Elimino ", players[turn_index]['username'], " (",turn_index,")"
		players.remove(players[turn_index])
		if turn_index >= len(players): #Nel caso in cui ha fatto crash l'ultimo della lista
			turn_index = turn_index % len(players)
		turn_index = ((turn_index + 1) % len(players))
	else:
		return "Unexcepted player", 400
	if players[turn_index]['username'] == my_player_name:
		print "\n>>> DEVI GIOCARE TU <<<\n"
		my_turn = True
	print "Adesso e' il turno di: " + players[turn_index]['username']
	return "", 200

#Metodo invocato dall'utente in locale (browser)
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

#Metodo che fa il pop di n carte dal mazzo e le restituisce come lista
def pesca(n):
	pescate = []
	for i in range(0,n):
		pescate.append(deck.pop(0))
	return pescate

#Metodo invocato dal nodo che dubita
@app.route('/doubted/<string:username>', methods = ['PUT'])
def doubted(username): #il param. e' l'username di chi invia il messaggio
	reset_timer()
	global table
	global my_turn
	global turn_index
	global doubtp
	global doubtStatus
	doubtp = username
	#E' arrivata la giocata dal successivo a quello da cui me l'aspettavo
	if players[(turn_index+1)%len(players)]['username'] == username:
		players.remove(players[turn_index])
		if turn_index >= len(players):
			turn_index = turn_index % len(players)
	elif players[turn_index]['username'] != username:
		return "Unexpected player", 400
	doubterIndex = turn_index
	print "Doubter = ", doubterIndex, players[doubterIndex]
	
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
			print "\n", players[turn_index]['username'], "ha dubitato bene"
			doubtStatus = 0;
			penalizatedIndex = prevIndex
			penalization = 3
			nextPlayerIndex = doubterIndex
			break
	else:
		#Dubitato male
		print "\n", players[turn_index]['username'], "ha dubitato male"
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
		print "Ho pescato " + str(penalization) + " carte: la mia mano"
		for c in hand:
			print "ID="+str(c.card_id)+" Y="+str(c.year)
	#Tutti i giocatori aggiornano il counter delle carte del penalizzato
	players[penalizatedIndex]['n_cards'] = str(int(players[penalizatedIndex]['n_cards']) + penalization)
	#In ogni caso (sia dubitato bene, sia male) resetto il tavolo
	table = []
	table.append(deck.pop(0))
	print "Il mazzo ha", str(len(deck)), "carte"
	print "Nuovo tavolo: ID=" + str(table[0].card_id) + " Y=" + str(table[0].year)
	#Verifico se e' il mio turno
	turn_index = nextPlayerIndex
	if myIndex == turn_index:
		print "\n>>> DEVO GIOCARE IO!!! <<<\n"
		my_turn = True
	print "Adesso e' il turno di: " + players[turn_index]['username']
	return "",200


@app.route('/threads')
def threads():
	print enumerate()
	return str(enumerate())+"\n", 200

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
		print "Eccezione! Provo la porta: " + str(my_port)
		return False

if __name__ == "__main__":
	if len(sys.argv) == 1:
		my_ip = "127.0.0.1"
		server_ip = "127.0.0.1"
	elif len(sys.argv) == 3:
		my_ip = sys.argv[1]
		server_ip = sys.argv[2]
	else:
		print "Usage:", sys.argv[0], "<public IP><server IP>"
		exit(1)
	app.debug = True
	server_started = try_ports()
	while not server_started:
		server_started = try_ports()

	print "back to main"
	
	for t in enumerate():
		if currentThread() != t and t.__class__.__name__ != "_DummyThread":
			print "try joining: " + str(t)
			#t.join(1.0)
			if t.__class__.__name__ == "_Timer":
				t.cancel()
				print "timeout canceled!"
	sys.exit()
