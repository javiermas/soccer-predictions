import pandas as pd
import numpy as np
from pymongo import MongoClient


class Competitions(object):
    def __init__(self):
        client = MongoClient('127.0.0.1', 27018)
        self.db = client.soccer
        self.competitions = self.db.competitions

    def load(self, seasons=None):
        query = {}
        if seasons is not None:
            query = self.load_many_seasons(seasons)

        cursor = self.competitions.find(query)
        return pd.DataFrame(list(cursor))
    
    def seasons_exist(self, seasons):
        seasons_exist = list()
        for season in seasons:
            cursor = self.competitions.find_one({'season': season})
            season_data = pd.DataFrame(list(cursor))
            seasons_exist.append(season_data.empty)

        return np.array(seasons_exist)

    def load_many_seasons(self, seasons):
        return {'season': {'$in$': seasons}}

    def save(self, docs):
        for key, row in docs.iterrows():
            self.competitions.update({'id': row['id']}, 
                                     row.to_dict(), upsert=True)
    def get_competition_ids(self):
        cursor = self.competitions.distinct('id')
        ids = list(cursor)
        if not ids:
            print 'Warning: competitions collection is empty'

        ids = [id_ for id_ in ids if id_ not in [424]] # Intl
        return ids

    def update(self, doc):
        bulk = self.competitions.initialize_ordered_bulk_op()
        for record in self.competitions.find(snapshot=True):
            new_record = doc.loc[doc['competition'] == record['competition']]
            bulk.find({'team': record['competition']})\
                    .update({})


