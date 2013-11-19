#!../flask/bin/python
from flask import jsonify
class Game:

   """A game rappresentation"""

   def __init__(self, game_id=-1, creator="", player_n=0, p_list=[]):
   		self.game_id = game_id
   		self.creator = creator
   		self.p_list = []
   		if player_n in range(4,20):
   			self.player_n = player_n
   		else:
   			raise ValueError("player_n not in range")
   		if creator == "":
   			raise ValueError("no creator name")
   		else:
   			self.p_list.append(self.creator)

   def __str__(self):
   		str = "Game: game_id:%d, creator:%s, player_number:%d players:[" % (self.game_id, self.creator, self.player_n)
   		str += ",".join(self.p_list)
   		str += "]"
   		return str

   def add_player(self, player):
   		if len(self.p_list) < self.player_n:
   			self.p_list.append(player)
   		else:
   			ValueError("The game is full")

   def to_json(self):
   		return jsonify(game_id = self.game_id, creator = self.creator, player_n = self.player_n, p_list = self.p_list )

if __name__ == "__main__":
	a_game = Game(11,"stefano",5)
	print a_game.__dict__
	print a_game