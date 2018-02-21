import pandas as pd
from pymongo import MongoClient


class Fixtures(object):
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.db = client.soccer
        self.fixtures = self.db.fixtures

    def load(self):
        cursor = self.fixtures.find()
        return pd.DataFrame(list(cursor))

    def save(self, docs):
        for key, row in docs.iterrows():
            self.fixtures.update({'id': row['id']}, row.to_dict(), upsert=True)

    def get_competition_ids(self):
        cursor = self.fixtures.distinct('id')
        return list(cursor)

    def update(self, doc):
        bulk = self.fixtures.initialize_ordered_bulk_op()
        for record in self.fixtures.find(snapshot=True):
            new_record = doc.loc[doc['competition'] == record['competition']]
            bulk.find({'team': record['competition']})\
                    .update({})



