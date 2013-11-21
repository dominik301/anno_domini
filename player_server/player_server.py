#!../framework/bin/python
import requests
r = requests.get('http://localhost:5000/')
print(r.text)