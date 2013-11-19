#!flask/bin/python
from flask import request
class Player():

   """A Player rappresentation"""

   def __init__(self, username):
         if username == "":
            raise ValueError("no username")
         else:
            self.username = username
         #request.remote_addr mi ritorna l'ip del client che richiede il servizio libreria flask
         self.ip = request.remote_addr

   def __str__(self):
   		str = "Player: username:%s,ip:%s" %(self.username,self.ip)
   		return str

if __name__ == "__main__":
	a_player = Player("vincenzo")
	print a_player