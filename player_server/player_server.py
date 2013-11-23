#!../framework/bin/python
import requests
import random
from flask import Flask
from game_card import *

#mazzo di test
deck = []
for j in range(0,20):
	deck.append( Game_Card(j, "e_" + str(j)) ) 

#lista di giocatori per il testing
players = ["stefano","vincenzo","roberto"]

app = Flask(__name__)

@app.route("/")
def hello():
	return "sono il server_player\n"

@app.route('/createPlayer', methods = ['POST'])
def create_player():
	return "permette al giocatore di iscriversi al server di anno domini"

@app.route('/createGame', methods = ['POST'])
def create_game():
	return "permette ad un giocatore di creare una partita"

@app.route('/joinGame/<string:username>/<int:game_id>', methods = ['PUT'])
def join_g(username,game_id):
	return requests.put("http://localhost:5000/joinGame/username/game_id")

@app.route('/cards', methods = ['PUT'])
def sendCards():
	#lista di giocatori per il testing
	players = ["stefano","vincenzo","roberto"]
	#and len( deck ) >= (20 - the_game.player_n * 3)
	for p in players:
		send_c(get_randomCard(), p)

@app.route('/table', methods = ['PUT'])
def playFirstCard():
	#return dummy
	return None

#genera le carte da gioco iniziali di un giocatore
def get_randomCard():
	global deck
	n = 0
	player_cards = []
	#sto usando dei magic number (20 che sarebbe la grandezza del mazzo di prova e 3 la mano dei giocatori), come si definiscono le costanti in python
	while n < 3 :
		player_cards.append( deck.pop(random.choice(range(len(deck)))) )
		n = n + 1
	return player_cards

#invia una lista di carte ad un giocatore, per ora ci sono solo stampe di debug
def send_c(cards, player):
	print player + " received:\n",
	for c in cards:
		print c

if __name__ == "__main__":
	sendCards()
	print "deck dopo aver distribuito 9 carte"
	for deck_c in deck:
		print deck_c
#r = requests.get('http://localhost:5000/')
#print(r.text)