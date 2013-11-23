#!../framework/bin/python
from flask import request, jsonify
import requests

class Player:

	"""A Player representation"""

	def __init__(self, username=None):
		if username == "":
			raise ValueError("no username")
		else:
			self.username = username
			#request.remote_addr mi ritorna l'ip del client che richiede il servizio libreria flask
			self.ip = request.remote_addr

	def __str__(self):
		str = "Player_username: %s, ip: %s" %(self.username, self.ip)
		return str

	def to_json(self):
		return jsonify(username = self.username, ip = self.ip)

if __name__ == "__main__":
	a_player = Player("vincenzo")
