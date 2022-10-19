#!../framework/bin/python
import json
import os
import signal
import _thread

from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
from game_card import *
from game import *
from deck import *
from player import * #for testing
from threading import currentThread, enumerate, Thread

gamesList = list()
'''lista dei giochi creati'''

_games_ = dict()
"""game list"""

_players_ = dict[str,Player]()
"""player list"""

index = 0
"""index of games"""

app = Flask(__name__, static_folder = "static")
io = SocketIO(app, async_mode=None)

def remove(gameId):
	global gamesList, _games_, _players_
	if gameId in _games_:
		for p in _games_[gameId].p_list:
			_players_.pop(p.username)
		gamesList.remove(_games_[gameId])
		_games_.pop(gameId)

@io.on('disconnect')
def disconnect():
	for p in _players_:
		if request.sid == _players_[p].sid:  # type: ignore
			return remove_player(p)

def remove_player(username):
	global _players_
	_players_.pop(username)

def terminate_app():
	'''qui eseguo la kill sul gruppo di processi attivi per questo player_server'''
	pid_g = os.getpgrp()
	os.killpg(pid_g, signal.SIGKILL)

@app.route("/")
def hello():
	return render_template("gui.html", sync_mode=io.async_mode)

@io.on("mano")
def return_hand():
	'''Polling dalla GUI per avere la propria mano'''
	for p in _players_:
		if request.sid == _players_[p].sid:  # type: ignore
			_games_[_players_[p].game_id].return_hand(request.sid)  # type: ignore
			break
	
@io.on("gameStatus")
def game_status():
	'''Polling dalla GUI per avere lo stato del gioco (in attesa o iniziato)'''
	for p in _players_:
		if request.sid == _players_[p].sid:  # type: ignore
			if _games_.get(_players_[p].game_id) == None:
				return
			status = _games_[_players_[p].game_id].game_status()
			emit("gameStatusResponse",json.dumps(status),room=request.sid,namespace='/')  # type: ignore
			break

@io.on("playerCards")
def playerCards():
	'''Polling dalla GUI per avere il numero delle carte degli altri'''
	for p in _players_:
		if request.sid == _players_[p].sid:  # type: ignore
			cards = _games_[_players_[p].game_id].playerCards()
			emit('playerCards', cards, room=request.sid, namespace='/')  # type: ignore
			if len(_games_[_players_[p].game_id].p_list) < 2:
				remove(_players_[p].game_id)
			break

@io.on("bancoOrDoubt")
def bancoOrDoubt():
	'''Polling dalla GUI per avere lo stato del gioco dopo l'inizio'''
	for p in _players_:
		if request.sid == _players_[p].sid:  # type: ignore
			status = _games_[_players_[p].game_id].bancoOrDoubt()
			emit("gameStatusBoD",status,room=request.sid,namespace='/')  # type: ignore
			break

@io.on('gamesList')
def gameList():
	'''Metodo invocato dal browser web'''
	result = json.dumps([game.to_dict() for game in gamesList])
	emit('gameList',result, room=request.sid,namespace="/")  # type: ignore

@io.on('createGame')
def create_g(username, n_players):
	global index
	global _games_
	global gamesList
	if username in _players_:
		try:
			new_g = Game(index, _players_[username], int(n_players),[])
			new_g.game_id = index
			_players_[username].game_id = index
		except PlayersNumberRangeException:		
			emit("createGameError","Wrong number of players\n",room=request.sid,namespace="/")  # type: ignore
			return
		except CreatorNotFoundException:
			emit("createGameError","Creator non found\n",room=request.sid,namespace="/")  # type: ignore  # type: ignore
			return
		_games_[index] = new_g
		print(index, new_g, new_g.game_id)
		#informo tutti i players iscritti al server della creazione del nuovo gioco
		gamesList = []
		for key in _games_:
			gamesList.append(_games_[key])
		index = index + 1
	else:
		emit("createGameError","Unknown username\n",room=request.sid,namespace="/")  # type: ignore
		return
	emit("createGameSuccess",str(index-1),room=request.sid,namespace="/")  # type: ignore

@io.on('joinGame')
def join_g(username, game_id):
	#Controllo che username e game_id siano stati passati correttamente
	if username not in _players_ or game_id not in _games_:
		return
	player = _players_[username]
	game = _games_[game_id]
	try:
		game.add_player(player)
		player.game_id = game.game_id
	except PlayersNumberReachedException:
		return
	except UserSubscriptionException:
		return
	if game.player_n == len(game.p_list):
		for i in game.p_list:
			emit('startGame',json.dumps(game.p_list, default=lambda o: o.__dict__), room=i.sid,namespace='/')
		game.start_g()

@io.on('playCard')
def playCard(card_id,card_pos):
	'''Metodo invocato dal browser web per giocare una carta'''
	for p in _players_:
		if request.sid == _players_[p].sid:  # type: ignore
			_games_[_players_[p].game_id].playCard(card_id,card_pos)
			break

@io.on('doubt')
def doubt(): 
	'''il param. e' l'username di chi invia il messaggio
	Metodo invocato dal nodo che dubita'''
	for p in _players_:
		if request.sid == _players_[p].sid:  # type: ignore
			_games_[_players_[p].game_id].doubt()
			break

@io.on('createPlayer')
def create_p(username):
	global _players_
	new_p = Player(username, request.sid)  # type: ignore
	if new_p.username not in _players_:
		for p in _players_:
			if _players_[p].sid == new_p.sid:
				emit('createErr',"You have already been registered\n", room=new_p.sid)
				return
		_players_[new_p.username] = new_p
	else:
		emit('createErr',"Username already chosen\n", room=new_p.sid,namespace='/')
		return
	emit('createSuccess',"Registriert\n", room=new_p.sid,namespace='/')

if __name__ == "__main__":
	_thread.start_new_thread(lambda: io.run(app, debug=False), ())

	for t in enumerate():
		if currentThread() != t and t.__class__.__name__ != "_DummyThread" and t.__class__.__name__ != "_MainThread":
			print("try joining: " + str(t))
			#t.join()
			if t.__class__.__name__ == "_Timer":
				t.cancel() # type: ignore
				print("timeout canceled!")
