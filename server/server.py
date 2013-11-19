#!../flask/bin/python
from game import *
from flask import Flask
from flask import jsonify

app = Flask(__name__)

a_game = Game(11,"stefano",5)

@app.route("/")
def hello():
	return a_game.to_json()

if __name__ == '__main__':
	app.debug = True
	app.run()