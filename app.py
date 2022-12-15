import pandas as pd
from pymongo import MongoClient

from flask import Flask
app = Flask(__name__)

CONNECTION_STRING = "mongodb+srv://recipe-gen-auth:nuvklQyHU5qPNi1D@recipe-gen.kbrot3f.mongodb.net/?retryWrites=true&w=majority"

def get_database():
    client = MongoClient(CONNECTION_STRING)
    return client.recipe_gen

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/test')
def hello_world():
    db = get_database()
    return db.find({'category': 'meat'})