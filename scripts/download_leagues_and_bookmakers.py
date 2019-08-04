from configparser import ConfigParser

import soccerlearn.data.sport_monks.downloading as dl


parser = ConfigParser()
parser.read('config.cfg')
token = parser.get('sportmonks', 'token')

dl.download_leagues(token, path='data/leagues.csv')
dl.download_bookmakers(token, path='data/bookmakers.csv')
