#!../framework/bin/python
import json
from flask import jsonify
class Game_Card():
	"""A game card reppresentation"""

	def __init__(self,year=-1, event=None, card_id=-1):
		if (year >= 0 and year <= 2013) and event != None and card_id > -1:
			self.year = year
			self.event = event
			self.card_id = card_id
		else:
			raise ValueError("Can't creat the game card: bad year event or empy event")

	def __str__(self):
		return "year: " + str(self.year) + " event: " + self.event +" card_id "+ str(self.card_id)

	def to_json(self):
		return jsonify(id = self.card_id, year = self.year, event = self.event)

if __name__ == "__main__":
	deck = []
	for j in range(0,20):
		deck.append( Game_Card(j, "e_" + str(j), j) ) 
	for c in deck:
		print(c)
