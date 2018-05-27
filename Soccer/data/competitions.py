import pandas as pd
import numpy as np
from pymongo import MongoClient
from Soccer.data.connection import Connection


class Competitions(object):
    def __init__(self):
        connection = Connection()
        self.db = connection.get_connection()
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
            seasons_exist.append(cursor is not None)

        return seasons_exist

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



