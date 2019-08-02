from pymongo import MongoClient


class Connection(object):
    def __init__(self, host='127.0.0.1', port=27017):
        self.client = MongoClient(host, port)

    def get_connection(self, db='soccer'):
        return self.client[db]

