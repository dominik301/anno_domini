#!../framework/bin/python
from flask import jsonify
from flask import Flask
from player import *
import json

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

	def __init__(self, game_id=-1, creator=None, player_n=0, started=False, p_list=[]):
		self.game_id = game_id
   		self.creator = creator
   		self.p_list = []
   		if player_n in range(4,20):
   			self.player_n = player_n
   		else:
   			raise PlayersNumberRangeException("Number of players not in range")
   		if creator is None or not isinstance(creator, Player):
   			raise CreatorNotFoundException("Missing creator or not found")
   		else:
			self.p_list.append(self.creator)

	def __str__(self):
   		g_str = "Game: game_id:%d, creator:%s, player_number:%d players:[" % (self.game_id, self.creator.username, self.player_n)
   		for i in range(len(self.p_list)):
   			if i == (len(self.p_list) - 1):
   				g_str += "<Name: " + self.p_list[i].username + " Ip: " + str(self.p_list[i].ip) + ">"
   			else:
   				g_str += "<Name: " + self.p_list[i].username + " Ip: " + str(self.p_list[i].ip) + "> | "
   		g_str += "]"
   		return g_str

	def add_player(self, player):
   		if len(self.p_list) >= self.player_n:
			raise PlayersNumberReachedException("Number of players reached")
		else:
			if player in self.p_list:
				raise UserSubscriptionException("The player is already subscripted")
			else:
				self.p_list.append(player)

	def remove_player(self, player):
		if player == self.creator:
			raise CreatorUnsubscriptionException("The creator cannot be unsubscribed");
		if player in self.p_list:
			self.p_list.remove(player)
		else:
			raise UserNotFoundException("The player is not subscripted")

	def start_game(self):
   		self.started = True
		#TODO implementare l'invio dei messaggi ai nodi del SD per iniziare la partita

	def to_json(self):
		return jsonify(game_id = self.game_id, creator = json.dumps(vars(self.creator)), player_n = self.player_n, p_list = json.dumps(self.p_list, default=lambda o: o.__dict__) )

if __name__ == "__main__":
	app = Flask(__name__)
	with app.test_request_context():
		stefano = Player("Stefano")
		roberto = Player("Roberto")
		vincenzo = Player("Vincenzo")
		mario = Player("Mario")
		ale = Player("Ale")
		a_game = Game(11, stefano, 5)
		a_game.add_player(vincenzo)
		try:
			a_game.add_player(vincenzo)
		except:
			print "Vincenzo non aggiunto"
		a_game.add_player(roberto)
		a_game.add_player(ale)
		try:
			a_game.add_player(vincenzo)
		except:
			print "Vincenzo non aggiunto"
		a_game.add_player(mario)
		print a_game
		a_game.remove_player(mario)
		print a_game
		a_game.remove_player(ale)
		print a_game

