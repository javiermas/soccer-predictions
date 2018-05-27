import pandas as pd
from Soccer.data.connection import Connection


class Players(object):
    def __init__(self, host='127.0.0.1', port=27017):
        connection = Connection(host, port)
        self.db = connection.get_connection()
        self.players = self.db.players

    def load(self):
        cursor = self.players.find()
        return pd.DataFrame(list(cursor))

    def save(self, docs):
        for key, row in docs.iterrows():
            self.players.update({'id': row['id']}, row.to_dict(), upsert=True)


