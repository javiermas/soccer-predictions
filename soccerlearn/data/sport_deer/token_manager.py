import time
import json
import os
import requests


class TokenManager(object):
    def __init__(self):
        self.refresh_token = os.environ['REFRESH_TOKEN']
    
    def get_access_token(self, path):
        access_token, usable = self.get_last_access_token(self.refresh_token, path)
        if not usable:
            access_token = self.get_new_access_token(self.refresh_token)
            self.save_access_token(access_token, path)
        
        return access_token['new_access_token']

    @staticmethod
    def get_last_access_token(refresh_token, path):
        files = os.listdir(path)
        if not files:
            return None, False

        last_update = max([int(f.split('access_token_')[1].split('.json')[0]) 
                           for f in files if f.endswith('json')])
        usable = round(time.time()) < (last_update + 30*60)
        with open(path+'access_token_{}.json'.format(last_update), 'r') as token:
            access_token = json.load(token)

        return access_token, usable

    @staticmethod
    def get_new_access_token(refresh_token):
        query_access_token = 'https://api.sportdeer.com/v1/accessToken?refresh_token={}'.format(refresh_token)
        req = requests.request('GET', query_access_token)
        return req.json()

    @staticmethod
    def save_access_token(access_token, path):
        with open(path+'access_token_{}.json'.format(round(time.time())), 'w') as js:
            json.dump(access_token, js)
