#!../framework/bin/python
import random
from flask import jsonify
from flask_socketio import emit
from player import *
from game_card import *
from deck import *
import json
from threading import Timer
from player_server import remove, app, remove_player

class UserNotFoundException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value

class CreatorUnsubscriptionException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value

class PlayersNumberRangeException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value

class PlayersNumberReachedException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value	

class CreatorNotFoundException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value

class UserSubscriptionException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value

class Game:
	"""A game representation"""

	def __init__(self, game_id=-1, creator=None, player_n=0, p_list=[]):
		self.game_id = game_id
		self.creator = creator
		self.p_list = p_list
		if player_n in range(2,20):
			self.player_n = player_n
		else:
			raise PlayersNumberRangeException("Number of players not in range")
		if creator is None or not isinstance(creator, Player):
			raise CreatorNotFoundException("Missing creator or not found")
		else:
			self.p_list.append(self.creator)
		#timer (corrente: viene di volta in volta rinnovato con i reset) di ogni giocatore
		self.player_timer = self._timer(False)
		self.deck = Deck
		'''mazzo'''
		
		self.table = []
		'''le carte sul tavolo'''
		
		self.tablePreDoubt = []
		'''le carte sul tavolo prima del dubbio'''
		
		self.game_id = 0
		'''id del gioco'''
		
		self.hands = dict[str,list[Game_Card]]()
		'''carte che ho in mano'''
		
		self.winner = ""
		'''variabile dell'eventuale vincitore'''
		
		self.doubtp = ""
		'''variabile per il polling del dubbio'''

		self.doubtStatus = 0
		'''variabile per lo stato del dubbio 0 bene 1 male'''

		self.turn_index = 0
		'''indice dei turni, mi serve per capire chi e' crashato'''

		self.timeOut = {}
		'''variabile per stabilire il mio crash'''

		self.started = False

	def __str__(self):
		g_str = "Game: game_id:%d, creator:%s, player_number:%d players:[" % (self.game_id, self.creator.username, self.player_n) # type: ignore
		for i in range(len(self.p_list)):
			if i == (len(self.p_list) - 1):
				g_str += "<Name: " + self.p_list[i].username + " Ip: " + str(self.p_list[i].sid) + ">"
			else:
				g_str += "<Name: " + self.p_list[i].username + " Ip: " + str(self.p_list[i].sid) + "> | "
		g_str += "]"
		return g_str

	def add_player(self, player : Player):
		if len(self.p_list) >= self.player_n:
			raise PlayersNumberReachedException("Number of players reached")
		else:
			if player in self.p_list:
				raise UserSubscriptionException("The player is already subscripted")
			else:
				self.p_list.append(player)

	def to_json(self):
		return jsonify(game_id = self.game_id, creator = json.dumps(vars(self.creator)), player_n = self.player_n, p_list = json.dumps(self.p_list, default=lambda o: o.__dict__) )

	def to_dict(self):
		return {"game_id": self.game_id, "creator": {"username": self.creator.username}, "player_n": self.player_n, "started": self.started}

	def reset(self):
		remove(self.game_id)

	def _timer(self, plus : bool):
		if plus:
			return Timer(100.0, self.time_out)
		else:
			return Timer(90.0, self.time_out)

	def time_out(self):
		self.timeOut[self.turn_index] = True

		print("TIMEOUT: der Spieler musste diese Runde spielen:" + str(self.turn_index) +":"+ self.p_list[self.turn_index].username)
		status = self.myTimeOut()
		with app.test_request_context():
			print(status,self.p_list[self.turn_index].sid)
			self.p_list.remove(self.p_list[self.turn_index])
			if len(self.p_list) < 2:
				print("Zu wenige Spieler, das Spiel kann nicht weitergehen")
				return
			if self.turn_index >= len(self.p_list): #Nel caso in cui ha fatto crash l'ultimo della lista
				self.turn_index = self.turn_index % len(self.p_list)
		self.reset_timer(False)

	def reset_timer(self, plus : bool):
		self.player_timer.cancel()
		self.player_timer = self._timer(plus)
		self.player_timer.start()

	def myTimeOut(self):
		if self.turn_index in self.timeOut and self.timeOut[self.turn_index]:
			return json.dumps({"my_timeout": True})
		else:
			return json.dumps({"my_timeout": False})
	
	def return_hand(self, sid):
		'''Polling dalla GUI per avere la propria mano'''
		_hand = []
		for p in self.p_list:
			if p.sid == sid:
				_hand = self.hands[p.username]
		emit("mano",json.dumps(_hand, default=lambda o: o.__dict__),room=sid,namespace='/')
		
	def game_status(self):
		'''Polling dalla GUI per avere lo stato del gioco (in attesa o iniziato)'''
		if len(self.table) == 0 :
			return {'status' : 0}
		return {'status' : 1}

	def playerCards(self):
		cards_dict = {}
		i = 0
		for p in self.p_list:
			cards_dict[i] = {'username': p.username, 'n_cards' : p.n_cards}
			i = i+1
		return json.dumps(cards_dict, default=lambda o: o.__dict__)
		
	def bancoOrDoubt(self):
		if self.doubtp != "": #Restituisco lo stato del dubito
			toReturn = {'status': 'doubt', 'doubter': str(self.doubtp), 'doubtResult': str(self.doubtStatus), 'table': self.tablePreDoubt}
			self.resetDoubt()
			for p in self.p_list:
				emit('bancoOrDoubt', json.dumps(toReturn, default=lambda o: o.__dict__),room=p.sid,namespace='/')
		else: #Restituisco il banco
			jsonTurno = {'winner': self.winner, 'turn': 0, 'turn_index': self.turn_index}
			toReturn = {'status': 'normal', 'turn': jsonTurno , 'table': self.table}
		return json.dumps(toReturn, default=lambda o: o.__dict__)

	def playCard(self, card_id,card_pos):
		my_player_name = self.p_list[self.turn_index].username
		_hand = self.hands[my_player_name]
		for card in _hand :
			if card.card_id == card_id :
				cardToSend = card
				_hand.remove(card)
				break
		else:
			return
		self.playedCard(my_player_name, cardToSend.year, cardToSend.event, cardToSend.card_id, card_pos)
	
	def start_g(self):
		if self.started:
			return
		self.started = True
		self.turn_index = 0
		self.table.append(self.deck.pop(random.choice(list(range(len(self.deck))))))
		for p in self.p_list:
			cards = self.get_randomCards()
			self.hands[p.username] = cards
		self.player_timer.start()		

	def get_randomCards(self):
		'''Genera le carte da gioco iniziali di un giocatore rimuovendole dal deck'''
		player_cards = []
		#sto usando dei magic number (20 che sarebbe la grandezza del mazzo di prova e 3 la mano dei giocatori), come si definiscono le costanti in python
		for n in range (0,7) :
			player_cards.append( self.deck.pop(random.choice(list(range(len(self.deck))))) )
		return player_cards	

	def playedCard(self, username : str, year : int, event, card_id : int, position):
		"""Metodo invocato da un altro player_server
		L'username serve perche' nel test in localhost l'ip e' sempre lo stesso e non si riesce a riconoscere gli utenti"""
		print("Karte gespielt von", username)
		#la prima cosa che faccio e' resettare il timer del timeout
		self.reset_timer(False)
		cardToInsert = Game_Card(year, event, card_id)
		self.table.insert(position, cardToInsert)
		if self.p_list[self.turn_index].username == username:
			self.p_list[self.turn_index].n_cards -= 1
			if self.p_list[self.turn_index].n_cards == 0: #Auto-dubito (ATTENZIONE: avviene localmente in tutti i nodi senza scambio di msg)
				winner_index = self.turn_index
				self.turn_index = ((self.turn_index + 1) % len(self.p_list))
				returned = self.doubt()
				if returned=="End":
					self.winner = self.p_list[winner_index].username
					print("\nIl gioco e' finito! Il vincitore e' " + self.winner + "\n")
					self.reset()
					emit('playedCard', room=self.p_list[self.turn_index].sid, namespace='/') #TODO
					return
			else:
				self.turn_index = ((self.turn_index + 1) % len(self.p_list))
		#il giocatore da cui mi aspettavo la giocata e' crashato: mi e' arrivata la giocata da quello successivo
		elif self.p_list[(self.turn_index+1) % len(self.p_list)].username == username:
			print("Es spielte der nächste Spieler, anders als ich erwartet hatte")
			print("Elimino ", self.p_list[self.turn_index].username, " (",self.turn_index,")")
			self.p_list.remove(self.p_list[self.turn_index])
			remove_player(self.p_list[self.turn_index].username)
			if self.turn_index >= len(self.p_list): #Nel caso in cui ha fatto crash l'ultimo della lista
				self.turn_index = self.turn_index % len(self.p_list)
			self.turn_index = ((self.turn_index + 1) % len(self.p_list))
		else:
			return
		print("Jetzt ist an der Reihe: " + self.p_list[self.turn_index].username)
		for p in self.p_list:
			emit('playedCard', room=p.sid, namespace='/')
		return
	
	def pesca(self, n:int):
		'''Metodo che fa il pop di n carte dal mazzo e le restituisce come lista'''
		pescate = []
		for _ in range(0,n):
			pescate.append(self.deck.pop(0))
		return pescate

	def doubt(self): 
		'''il param. e' l'username di chi invia il messaggio'''
		self.reset_timer(True)
		if len(self.table) < 2:
			return ""
		self.doubtp = self.p_list[self.turn_index].username
		self.tablePreDoubt = self.table
		doubterIndex = self.turn_index
		print("Doubter = ", doubterIndex, self.p_list[doubterIndex])
		
		prevIndex = doubterIndex - 1
		if prevIndex == -1:
			prevIndex = len(self.p_list) - 1
		
		for i in range(0, len(self.table) - 1):
			if self.table[i].year > self.table[i+1].year:
				#Il dubbio era fondato: si penalizza il precedente nella mano
				print("\n", self.p_list[self.turn_index].username, "hat richtig gezweifelt")
				self.doubtStatus = 0
				penalizatedIndex = prevIndex
				penalization = 3
				nextPlayerIndex = doubterIndex
				break
		else:
			#Dubitato male
			print("\n", self.p_list[self.turn_index].username, "hat zu Unrecht gezweifelt")
			self.doubtStatus = 1
			#Puo' essere che il gioco sia finito (siamo in auto-dubito e l'ultimo player ha 0 carte)
			if self.p_list[prevIndex].n_cards == 0:
				return "End"
			#Gioco non finito: colui che ha dubitato deve essere penalizzato
			penalizatedIndex = doubterIndex
			penalization = 2
			nextPlayerIndex = (doubterIndex + 1) % len(self.p_list)
		pescate = self.pesca(penalization)
		_hand = self.hands[self.p_list[penalizatedIndex].username]
		for c in pescate:
			_hand.append(c)
		print("Spieler hat " + str(penalization) + " Karten gezogen")
		#Tutti i giocatori aggiornano il counter delle carte del penalizzato
		self.p_list[penalizatedIndex].n_cards += penalization
		#So oder so (ob gut oder schlecht gezweifelt) habe ich die Tabelle zurückgesetzt 
		#und legen Sie die restlichen Karten am Ende des Stapels ein
		for c in self.table:
			self.deck.append(c)
		self.table = []
		self.table.append(self.deck.pop(0))
		#Verifico se e' il mio turno
		self.turn_index = nextPlayerIndex
		print("Jetzt ist an der Reihe: " + self.p_list[self.turn_index].username)
		return ""

	def resetDoubt(self):
		if self.doubtp != "":
			self.doubtp = ""

	def get_players(self):
		players_dict = dict((player.username, player.sid) for player in self.p_list) # type: ignore
		return jsonify(players_dict)
