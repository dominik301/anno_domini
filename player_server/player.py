#!../framework/bin/python
from flask import request, jsonify
import json
import requests

class Player:

	"""A Player representation"""

	def __init__(self, username=None, ip=""):
		if username == "" or ip == "":
			raise ValueError("no username or missing ip")
		else:
			self.username = username
			#request.remote_addr mi ritorna l'ip del client che richiede il servizio libreria flask
			self.ip = ip
	def __str__(self):
		str = "Player_username: %s, ip: %s" %(self.username, self.ip)
		return str

	def to_json(self):
		return jsonify(username = self.username, ip = self.ip)

if __name__ == "__main__":
	a_player = Player("vincenzo")
