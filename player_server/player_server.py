#!../framework/bin/python
import requests
from flask import Flask

app = Flask(__name__)
server_ip = "localhost"
server_port = "5000"

@app.route("/")
def hello():
	return "sono il server_player\n"

@app.route('/createPlayer/<string:username>', methods = ['POST'])
def create_p(username):
	if username != "":
		req = requests.post("http://"+server_ip+":"+server_port+"/createPlayer/"+username)
		return req.status_code
	else:
		return "",400

@app.route('/createGame/<string:username>/<int:n_players>', methods = ['POST'])
def create_g(username, n_players):
	if username != "" and n_players >=0:
		req = requests.post("http://"+server_ip+":"+server_port+"/createGame/"+username+"/"+str(n_players))
		return req.status_code
	else:
		return "",400

@app.route('/joinGame/<string:username>/<int:game_id>', methods = ['PUT'])
def join_g(username,game_id):
	return requests.put("http://localhost:5000/joinGame/username/game_id")

if __name__ == '__main__':
	app.debug = True
	app.run()

