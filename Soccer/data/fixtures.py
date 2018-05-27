import pandas as pd
from pandas import DataFrame
from pymongo import MongoClient
from Soccer.data.connection import Connection


class Fixtures(object):
    def __init__(self):
        connection = Connection()
        self.db = connection.get_connection()
        self.competitions = self.db.competitions
        self.fixtures = self.db.fixtures

    def load(self):
        cursor = self.fixtures.find()
        data = DataFrame(list(cursor)).drop('_id', axis=1)\
            .set_index(['competition_id', 'date'])
        return data

    def save(self, docs):
        for key, row in docs.iterrows():
            self.fixtures.update({'id': row['id']}, row.to_dict(), upsert=True)

    def get_competition_ids(self):
        cursor = self.fixtures.distinct('id')
        return list(cursor)

    def fixtures_in_competitions_exist(self, competitions):
        fixtures_in_competitions_exist = list()
        for competition in competitions:
            cursor = self.fixtures.find_one({'competition_id': competition})
            fixtures_in_competitions_exist.append(cursor is not None)

        return fixtures_in_competitions_exist

    def update(self, doc):
        bulk = self.fixtures.initialize_ordered_bulk_op()
        for record in self.fixtures.find(snapshot=True):
            new_record = doc.loc[doc['competition'] == record['competition']]
            bulk.find({'team': record['competition']})\
                    .update({})



