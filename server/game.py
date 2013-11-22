#!../framework/bin/python
from flask import jsonify
from flask import Flask
from player import *
import json

class Game:

   """A game rappresentation"""

   def __init__(self, game_id=-1, creator=None, player_n=0, started=False, p_list=[]):
   		self.game_id = game_id
   		self.creator = creator
   		self.p_list = []
   		if player_n in range(4,20):
   			self.player_n = player_n
   		else:
   			raise ValueError("player_n not in range")
   		if creator is None:
   			raise ValueError("missing creator")
   		else:
   			try:
   				if isinstance(creator, Player):
   					self.p_list.append(self.creator)
   				else:
   					raise ValueError("creator is not isinstance of player")
   			except TypeError:
   				raise ValueError("Game constructor: TypeError exception")

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
   		if len(self.p_list) < self.player_n:
			#Controllo che il player non sia gia presente nella lista
			found = False
			for x in self.p_list:
				if player.username == x.username:
					found = True
					break
			if not found:
				self.p_list.append(player)
			else:
				 raise ValueError("The player is already subscripted")
   		else:
   			raise ValueError("The game is full")

   def start_game(self):
   		if self.p_list == self.player_number:
   			self.started = True
   		else:
   			print "the can't be started\n"

   def to_json(self):
         return jsonify(game_id = self.game_id, creator = json.dumps(vars(self.creator)), player_n = self.player_n, p_list = json.dumps(self.p_list, default=lambda o: o.__dict__) )

if __name__ == "__main__":
	app = Flask(__name__)
	with app.test_request_context():
		a_player = Player("Stefano")
		a_game = Game(11, a_player, 5)
		a_game.add_player(Player("Vincenzo")) 
