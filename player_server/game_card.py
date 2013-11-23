#!../framework/bin/python
class Game_Card:
	"""A game card reppresentation"""

	def __init__(self,year=-1, event=None):
		if (year >= 0 and year <= 2013) and event != None:
			self.year = year
			self.event = event
		else:
			raise ValueError("Can't creat the game card: bad year event or empy event")

	def __str__(self):
		return "year: " + str(self.year) + " event: " + self.event

if __name__ == "__main__":
	deck = []
	for j in range(0,20):
		deck.append( Game_Card(j, "e_" + str(j)) ) 
	for c in deck:
		print c
