import pandas as pd
import numpy as np
from pymongo import MongoClient

class Teams(object):
    def __init__(self):
        client = MongoClient('127.0.0.1', 27018)
        self.db = client.soccer
        self.teams = self.db.teams

    def load(self):
        cursor = self.teams.find()
        return pd.DataFrame(list(cursor))

    def teams_in_competitions_exist(self, competitions):
        teams_in_competitions_exist = list()
        for competition in competitions:
            cursor = self.teams.find_one({'competition_id': competition})
            team_data = pd.DataFrame(list(cursor))
            teams_in_competitions_exist.append(team_data.empty)

        return np.array(teams_in_competitions_exist)


    def save(self, docs):
        for key, row in docs.iterrows():
            self.teams.update({'team_id': row['team_id']}, row.to_dict(), 
                              upsert=True)


