import pandas as pd
import numpy as np
from pymongo import MongoClient
from Soccer.data.connection import Connection


class Teams(object):
    def __init__(self, host='127.0.0.1', port=27017):
        connection = Connection(host, port)
        self.db = connection.get_connection()
        self.teams = self.db.teams

    def load(self):
        cursor = self.teams.find()
        return pd.DataFrame(list(cursor))

    def teams_in_competitions_exist(self, competitions):
        teams_in_competitions_exist = list()
        for competition in competitions:
            cursor = self.teams.find_one({'competition_id': competition})
            teams_in_competitions_exist.append(cursor is not None)

        return teams_in_competitions_exist

    def save(self, docs):
        for key, row in docs.iterrows():
            self.teams.update({'unique_id': key}, row.to_dict(), 
                              upsert=True)


