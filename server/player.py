#!../framework/bin/python
from flask import jsonify

class Player:

	"""A Player representation"""

	def __init__(self, username="", sid=None, n_cards=7, game_id=-1):
		if username == "" or sid==None:
			raise ValueError("no username or missing sid")
		else:
			self.username = username
			#request.remote_addr mi ritorna l'ip del client che richiede il servizio libreria flask
			self.sid = sid
			self.n_cards = n_cards
			self.game_id = game_id
	def __str__(self):
		str = "Player_username: %s, sessid: %s, n_cards: %d" %(self.username, self.sid, self.n_cards)
		return str

	def to_json(self):
		return jsonify(username = self.username, sid = self.sid, n_cards = self.n_cards, game_id = self.game_id)
