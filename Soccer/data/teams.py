import pandas as pd
from pymongo import MongoClient

class Teams(object):
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.db = client.soccer
        self.teams = self.db.teams

    def load(self):
        cursor = self.teams.find()
        return pd.DataFrame(list(cursor))

    def save(self, docs):
        for key, row in docs.iterrows():
            self.teams.update({'team_id': row['team_id']}, row.to_dict(), 
                              upsert=True)


