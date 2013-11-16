class Game:

   'A game rappresentation'

   def __init__(self, game_id, creator, player_n):
   		self.game_id = game_id
   		self.creator = creator
   		self.player_n = player_n

   def __str__(self):
   		return "Game: game_id %d, creator %s, player number %d" % (self.game_id, self.creator, self.player_n)

if __name__ == "__main__":
	a_game = Game(11,"stefano",5)
	print a_game