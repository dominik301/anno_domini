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

#id del gioco
game_id = 0

#carte che ho in mano
hand = []

app = Flask(__name__)
server_ip = "127.0.0.1"
server_port = 5000

@app.route("/")
def hello():
	req=requests.post('http://localhost:5010/')
	print req.status_code
	return "sono il server_player ip: " + server_ip + " porta: " + str(server_port) + "\n"


@app.route('/createPlayer/<string:username>', methods = ['POST'])
def create_p(username):
	global my_player_name
	if username != "":
		req = requests.post("http://"+server_ip+":5000/createPlayer/"+username+"/"+str(server_port))
		my_player_name = username
		return "", req.status_code
	else:
		return "",400

@app.route('/createGame/<int:n_players>', methods = ['POST'])
def create_g(n_players):
	if my_player_name != "" and n_players >=1:
		req = requests.post("http://"+server_ip+":5000/createGame/"+my_player_name+"/"+str(n_players))
		global game_id
		game_id = int(req.text)
		return "", req.status_code
	else:
		return "",400

@app.route('/joinGame/<int:id_game>', methods = ['PUT'])
def join_g(id_game):
	req = requests.put("http://"+server_ip+":5000/joinGame/"+my_player_name+"/"+str(id_game))
	global game_id
	game_id = id_game
	return req.text,req.status_code
	
@app.route('/unsubscribe', methods = ['DELETE'])
def unsubscribe():
	if len(players) == 0:
		req = requests.delete("http://"+server_ip+":5000/unsubscribe/"+my_player_name+"/"+str(game_id))
		return "", req.status_code

@app.route('/startGame', methods = ['PUT'])
def start_g():
	global players
	global hand
	global table
	players = request.json #Restituisce lista di dizionari: ogni dizionario corrisponde a un player
	if players[0]['username'] == my_player_name:
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
	return "", 200

#genera le carte da gioco iniziali di un giocatore rimuovendole dal deck
def get_randomCards():
	global deck
	player_cards = []
	#sto usando dei magic number (20 che sarebbe la grandezza del mazzo di prova e 3 la mano dei giocatori), come si definiscono le costanti in python
	for n in range (0,7) :
		player_cards.append( deck.pop(random.choice(range(len(deck)))) )
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
		print "ID="+str(c.card_id)+" Y="+str(c.year)
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
		print "ID="+str(c.card_id)+" Y="+str(c.year)
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
	print "Il mazzo ha", str(len(deck)), "carte"
	#for c in deck:
	#	print c
	return "",200

#metodo richiamato dal browser per giocare una carta
@app.route('/playCard/<int:card_id>/<int:card_pos>', methods = ['PUT'])
def playCard(card_id,card_pos):
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
	for user in players:
		url = "http://"+user['ip']+":"+str(user['porta'])+"/playedCard"
		url = url + "/" + my_player_name + "/" + str(cardToSend.year) + "/" + str(cardToSend.event) + "/" + str(cardToSend.card_id) + "/" + str(card_pos)
		r = requests.put(url) #TODO: da' sempre "ok" come esito?! vedere se una delle put da errore e restituire 400
	return "ok"

#metodo richiamato da un altro nodo per comunicare la carta giocata
#l'username serve perche' nel test in localhost l'ip e' sempre lo stesso e non si riesce a riconoscere gli utenti
@app.route('/playedCard/<string:username>/<int:year>/<string:event>/<int:card_id>/<int:position>', methods = ['PUT'])
def playedCard(username, year, event, card_id, position):
	cardToInsert = Game_Card(year, event, card_id)
	table.insert(position, cardToInsert)
	print "\nBanco dopo la carta giocata"
	for i in table:	#only for test
		print "ID="+str(i.card_id)+" Y="+str(i.year)
	
	#Aggiorno il numero delle carte del player e controllo se e' il mio turno
	for x in players: #players e' una lista di dizionari
		if x['username'] == username:
			x['n_cards'] = str(int(x['n_cards']) - 1)
			print "\nIl giocatore", x['username'], "ha ora", x['n_cards'], "carte"
			if x['n_cards'] == "0": #Auto-dubito (ATTENZIONE: avviene localmente in tutti i nodi senza scambio di msg)
				returned = doubted(players[ ((players.index(x) + 1) % len(players)) ]['username'])
				if returned[0]=="Fine":
					print "\n IL GIOCO E' FINITO! IL VINCITORE E'" + x['username'] + "\n"
					return "", 200
			elif players[(players.index(x)+1) % len(players)]['username'] == my_player_name:
				print "\n>>> DEVO GIOCARE IO!!! <<<\n"
			break
	else:
		print "Non ho trovato il giocatore"
		return "", 400
	return "", 200

#Metodo invocato dall'utente in locale (browser)
@app.route('/doubt', methods = ['PUT'])
def doubt():
	if len(table) < 2:
		return "", 400
	for x in players: #lo invia anche a se' stesso
			url = "http://" + x['ip'] + ":" + str(x['porta']) + "/doubted/" + my_player_name
			r = requests.put(url)
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
	global table
	myIndex = -1
	doubterIndex = -1
	for user in players:
		if user['username'] == my_player_name:
			myIndex = players.index(user)
		if user['username'] == username:
			doubterIndex = players.index(user)
		if myIndex > -1 and doubterIndex > -1: #inutile continuare a cercare
			break
	prevIndex = doubterIndex - 1
	if prevIndex == -1:
		prevIndex = len(players) - 1
	
	for i in range(0, len(table) - 1):
		if table[i].year > table[i+1].year:
			#Il dubbio era fondato: si penalizza il precedente nella mano
			print "\nDubitato bene: carta ",table[i].card_id, " viene dopo ", table[i+1].card_id
			penalizatedIndex = prevIndex
			penalization = 3
			nextPlayerIndex = doubterIndex
			break
	else:
		#Dubitato male
		print "\nDubitato male"
		#Puo' essere che il gioco sia finito (siamo in auto-dubito e l'ultimo player ha 0 carte)
		if int(players[prevIndex]['n_cards']) == 0:
			return "Fine", 200
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
	if myIndex == nextPlayerIndex:
		print "\n>>> DEVO GIOCARE IO!!! <<<\n"
	return "",200

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
