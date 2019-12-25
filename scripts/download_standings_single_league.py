from configparser import ConfigParser
from argparse import ArgumentParser
from datetime import date
import soccerlearn.data.sport_monks.downloading as dl

argparser = ArgumentParser()
argparser.add_argument('--league', required=True)
args = argparser.parse_args()

parser = ConfigParser()
parser.read('config.cfg')
token = parser.get('sportmonks', 'token')

league_name = args.league 

dl.download_standings_single_league(token, league_name)
