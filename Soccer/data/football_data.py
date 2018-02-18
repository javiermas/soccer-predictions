import os
import copy
import requests
import time
import pandas as pd
import numpy as np
from Soccer.data.competitions import Competitions
from Soccer.data.teams import Teams
from Soccer.data.players import Players


class FootballData(object):
    '''
    Class FootballData. Provides a connection to the
    football-data API.

    Requires to set the football-api key as an environmental
    variable.
    '''

    def __init__(self):
        self.competitions = Competitions()
        self.teams = Teams()
        self.players = Players()
        self.url = 'http://api.football-data.org/v1/'
        self.headers = {'X-Auth-Token': os.environ['FOOTBALL_API_KEY']}
        self.path = os.getcwd().split('soccer_predictions')[0] + \
            'soccer_predictions/'

    def get_competition_fixtures(self, competition, season):
        '''Receives a competition id and a season and
        returns a dataframe with the corresponding
        fixtures.
        '''
        if isinstance(season, str):
            season = int(season)

        competition_id = np.unique(self.competitions_table.loc[
            (self.competitions_table['league'] == competition) &
            (self.competitions_table['season'] == season), 'id'])[0]
        query = self.url + 'competitions/%s/fixtures' % competition_id
        req = requests.request('GET', query, headers=self.headers)
        comp_json = req.json()
        try:
            fixtures = pd.DataFrame.from_dict(comp_json['fixtures'])
        except KeyError:
            print comp_json

        results = (fixtures['result'])
        results = results.apply(self._dict_to_dataframe)
        fixtures = pd.concat((fixtures, results), axis=1)
        fixtures = fixtures.drop('result', axis=1)
        fixtures = fixtures.assign(id=competition_id)
        fixtures_ranks = fixtures.apply(self._get_ranks_row, axis=1)
        fixtures = pd.concat((fixtures, fixtures_ranks), axis=1)
        return fixtures

    def _get_ranks_row(self, row):
        matchday = row['matchday']
        id = row['id']
        query = self.url + 'competitions/' + str(id) +\
            '/leagueTable/?matchday=' + str(matchday) 
        req = requests.request('GET', query, headers=self.headers)
        ranks = req.json()
        try:
            rank_home = [rank for rank in ranks['standing']
                         if rank['teamName'] == row['homeTeamName']][0]
            rank_away = [rank for rank in ranks['standing']
                         if rank['teamName'] == row['awayTeamName']][0]
        except:
            print ranks

        cols = ['playedGames', 'goals', 'goalsAgainst', 'points',
                'wins', 'draws', 'losses']
        rank_home = {k + '_home': v for k, v in rank_home.iteritems()
                     if k in cols}
        rank_away = {k + '_away': v for k, v in rank_away.iteritems()
                     if k in cols}
        ranks = copy.copy(rank_home)
        ranks.update(rank_away)
        return pd.Series(ranks)

    def extract_data(self):
        print 'Now extracting competition data'
        self.extract_competition_data()
        print 'Now extracting team data'
        self.extract_team_data()
        print 'Now extracting player data'
        self.extract_player_data()
        
    def extract_competition_data(self):
        self.competitions_table = self._create_competitions_table()
        self.competitions.save(
                self.competitions_table[['caption', 'id', 
                                        'league', 'year', 'season']])

    def extract_team_data(self):
        self.teams_table = self._create_teams_table()
        self.teams.save(
                self.teams_table[['code', 'shortName', 'name', 'team_id',
                                  'competition_id', 'squadMarketValue']])

    def extract_player_data(self):
        self.players_table = self._create_players_table()
        self.players.save(
                self.players_table[['dateOfBirth', 'marketValue',
                                    'name', 'nationality', 
                                    'position', 'team_id']])

    def _create_competitions_table(self):
        seasons = ['2015', '2016', '2017']
        competitions_data = map(self._get_competition_data, seasons)
        competitions_data = pd.concat(competitions_data).reset_index(drop=True)
        return competitions_data

    def _create_teams_table(self):
        competitions = self.competitions_table['id'].unique()
        teams_data = map(self._get_team_data, competitions)
        teams_data = pd.concat(teams_data).reset_index(drop=True)
        return teams_data

    def _create_players_table(self):
        unique_teams = self.teams_table['team_id'].unique()
        players_data = map(self._get_players_data, unique_teams)
        players_data = pd.concat(players_data).reset_index(drop=True)
        return players_data

    def _get_competition_data(self, season):
        query = self.url + 'competitions/?season=%s' % (season)
        req = requests.request('GET', query, headers=self.headers)
        try:
            competitions = pd.DataFrame(req.json())
        except ValueError:
            print 'Number of requests exceeded, now waiting.'
            time.sleep(60)
            req = requests.request('GET', query, headers=self.headers)
            competitions = pd.DataFrame(req.json())

        competitions['season'] = season
        return competitions

    def _get_team_data(self, competition_id):
        query = self.url + 'competitions/%s/teams' % competition_id
        req = requests.request('GET', query, headers=self.headers)
        teams_json = req.json()
        if teams_json.keys()[0] == 'error':
            return None

        data_teams = pd.DataFrame(teams_json['teams'])  # [cols_to_keep]
        data_teams['team_id'] = data_teams['_links']\
            .apply(self._get_team_code)
        data_teams['competition_id'] = competition_id
        return data_teams

    def _get_players_data(self, team_id):
        query = self.url + 'teams/%s/players' % team_id
        req = requests.request('GET', query, headers=self.headers)
        players_json = req.json()
        try:
            players_data = pd.DataFrame(players_json['players'])
        except KeyError:
            print 'Number of requests exceeded, now waiting.'
            time.sleep(60)
            req = requests.request('GET', query, headers=self.headers)
            players_json = req.json()
            players_data = pd.DataFrame(players_json['players'])

        players_data['team_id'] = team_id
        return players_data

    @staticmethod
    def _dict_to_dataframe(dict_):
        data_frame = pd.Series()
        data_frame['goals_away'] = dict_['goalsAwayTeam']
        data_frame['goals_home'] = dict_['goalsHomeTeam']
        return data_frame

    @staticmethod
    def _get_team_code(dict_):
        code = dict_['self']['href'].split('/')[-1]
        return code
