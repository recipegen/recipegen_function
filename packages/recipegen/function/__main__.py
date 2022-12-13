import os
from pymongo import MongoClient

def main(args):
    client = MongoClient(os.getenv('CONNECTION_STR')).recipe_gen
    return {'test': 'test'}