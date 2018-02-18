import pandas as pd
from pymongo import MongoClient

class Competitions(object):
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.db = client.soccer
        self.competitions = self.db.competitions

    def load(self):
        cursor = self.competitions.find()
        return pd.DataFrame(list(cursor))

    def save(self, docs):
        for key, row in docs.iterrows():
            self.competitions.update({'id': row['id']}, row.to_dict(), upsert=True)

    def update(self, doc):
        bulk = self.competitions.initialize_ordered_bulk_op()
        for record in self.competitions.find(snapshot=True):
            new_record = doc.loc[doc['competition'] == record['competition']]
            bulk.find({'team': record['competition']})\
                    .update({})



