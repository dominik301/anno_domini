#!../framework/bin/python
from flask import request, jsonify
import json
import requests

class Player:

	"""A Player representation"""

	def __init__(self, username=None, ip="", porta=5000):
		if username == "" or ip == "":
			raise ValueError("no username or missing ip")
		else:
			self.username = username
			#request.remote_addr mi ritorna l'ip del client che richiede il servizio libreria flask
			self.ip = ip
			self.porta = porta
	def __str__(self):
		str = "Player_username: %s, ip: %s, porta: %d" %(self.username, self.ip, self.porta)
		return str

	def to_json(self):
		return jsonify(username = self.username, ip = self.ip, porta = self.porta)

if __name__ == "__main__":
	a_player = Player("vincenzo", "0.0.0.0")
	print a_player.username, " ", a_player.ip, " ", a_player.porta
