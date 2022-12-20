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

@app.route('/get_item_details')
def get_item_details():
    db = get_database()
    items = request.args.getlist('item')

    item_jsons = list(db.item_details.find({'item': { "$in" : items }}))
    to_return = {}
    for item in item_jsons:
        to_return[item['item']] = {}
        to_return[item['item']]['category'] = item['category']
        to_return[item['item']]['tags'] = item['tags']
    
    return to_return

@app.route('/get_recipe_ids')
def get_recipe_ids():
    db = get_database()
    dietary = request.args.getlist('dietary')
    allergy = request.args.getlist('allergy')
    exclude_items = request.args.getlist('exclude_items')

    recipe_query = {}
    if len(allergy) > 0:
        recipe_query = {'allergens.immediate': {'$nin': allergy}}

    items_query = {}
    if len(dietary) > 0 and len(exclude_items) == 0:
        items_query = {'tags': {'$all': dietary}}
    elif len(dietary) == 0 and len(exclude_items) > 0:
        items_query = {'item': {'$nin': exclude_items}}
    elif len(dietary) > 0 and len(exclude_items) > 0:
        items_query = {'$and': [{'tags': {'$all': dietary}}, {'item': {'$nin': exclude_items}}]}

    recipe_jsons = list(db.recipe_details.find(recipe_query))
    item_jsons = list(db.item_details.find(items_query))
    item_list = [x['item'] for x in item_jsons]

    output_ids = []
    for recipe_json in recipe_jsons:
        found_bad_item = False
        for item in recipe_json['recipe']:
            if item['item'] not in item_list:
                found_bad_item = True
                break
        if not found_bad_item:
            output_ids.append(str(recipe_json['_id']))
    
    return {'ids': output_ids}

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