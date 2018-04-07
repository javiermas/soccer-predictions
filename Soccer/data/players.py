import pandas as pd
from pymongo import MongoClient

class Players(object):
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.db = client.soccer
        self.players = self.db.players

    def load(self):
        cursor = self.players.find()
        return pd.DataFrame(list(cursor))

    def save(self, docs):
        for key, row in docs.iterrows():
            self.players.update({'id': row['id']}, row.to_dict(), upsert=True)


