import pandas as pd
from pymongo import MongoClient
from bson.objectid import ObjectId

from flask import Flask, request
app = Flask(__name__)

CONNECTION_STRING = "mongodb+srv://recipe-gen-auth:nuvklQyHU5qPNi1D@recipe-gen.kbrot3f.mongodb.net/?retryWrites=true&w=majority"

def get_database():
    client = MongoClient(CONNECTION_STRING)
    return client.recipe_gen

@app.route('/')
def home():
    return 'Recipe Generation API'

@app.route('/get_item_cats')
def get_item_cats():
    db = get_database()
    items = request.args.getlist('item')

    item_jsons = list(db.item_category_map.find({'item': { "$in" : items }}))
    to_return = {}
    for item in item_jsons:
        if item['reviewed']:
            to_return[item['item']] = item['category']
        else:
            to_return[item['item']] = ''
    for item in items:
        if item not in to_return:
            to_return[item] = ''
    
    return to_return

@app.route('/get_recipe_ids')
def get_recipe_ids():
    db = get_database()
    bad_items = request.args.getlist('bad_items')

    recipe_jsons = list(db.recipe_details.find())
    output_ids = []
    for recipe_json in recipe_jsons:
        found_bad_item = False
        for item in recipe_json['recipe']:
            if item['item'] in bad_items:
                found_bad_item = True
                break
        if not found_bad_item:
            output_ids.append(str(recipe_json['_id']))
    
    return output_ids

@app.route('/get_recipe_ingredients')
def get_recipe_ingredients():
    db = get_database()
    ids = request.args.getlist('ids')
    ids = [ObjectId(x) for x in ids]

    recipe_jsons = list(db.recipe_details.find({'_id': { "$in" : ids }}))
    
    output_json = {}
    for i in range(len(recipe_jsons)):
        output_json[str(recipe_jsons[i]['_id'])] = recipe_jsons[i]['recipe']
    
    return output_json

@app.route('/get_recipe_details')
def get_recipe_details():
    db = get_database()
    ids = request.args.getlist('ids')
    ids = [ObjectId(x) for x in ids]

    recipe_jsons = list(db.recipe_details.find({'_id': { "$in" : ids }}))
    
    output_json = {}
    for i in range(len(recipe_jsons)):
        to_add = recipe_jsons[i].copy()
        del to_add['_id']
        del to_add['recipe']
        output_json[str(recipe_jsons[i]['_id'])] = to_add
    
    return output_json