import os
import copy
import requests
import datetime
import time
import pandas as pd
import numpy as np
from Soccer.data.competitions import Competitions
from Soccer.data.teams import Teams
from Soccer.data.players import Players
from Soccer.data.fixtures import Fixtures


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
        self.fixtures = Fixtures()
        self.url = 'http://api.football-data.org/v1/'
        self.headers = {'X-Auth-Token': os.environ['FOOTBALL_API_KEY']}
        self.path = os.getcwd().split('soccer_predictions')[0] + \
            'soccer_predictions/'


    def extract_data(self):
        print 'Now extracting competition data'
        self.extract_competition_data()
        print 'Now extracting team data'
        self.extract_team_data()
        # print 'Now extracting player data'
        # self.extract_player_data()
        print 'Now extracting fixture data'
        self.extract_fixture_data()

    def extract_competition_data(self):
        seasons = ['2015', '2016', '2017']
        seasons_exist = self._check_data_existence(seasons=seasons)
        seasons = seasons[~seasons_exist]
        cols = ['caption', 'id', 'league', 'year', 'season']
        for season in seasons:
            competition_data = self._get_competition_data(season)
            self.competitions.save(competition_data[cols])

    def extract_team_data(self):
        competitions = self.competitions.get_competition_ids()
        teams_in_competition_exist = self._check_data_existence(
                teams_in_competition=competitions)
        competitions = competitions[~teams_in_competition_exist]
        cols = ['code', 'shortName', 'name', 'team_id',
                'competition_id', 'squadMarketValue']
        for competition in competitions:
            team_data = self._get_team_data(competition)
            self.teams.save(team_data[cols])

    def extract_fixture_data(self):
        self.fixtures_table = self._create_fixtures_table()
        self.fixtures.save(self.fixtures_table)

    def extract_player_data(self):
        self.players_table = self._create_players_table()
        self.players.save(
                self.players_table[['dateOfBirth', 'marketValue',
                                    'name', 'nationality',
                                    'position', 'team_id']])

    def _check_data_existence(self, seasons=None, competitions=None,
                              teams_in_competitions=None, fixtures=None):
        if seasons is not None:
            return self.competitions.seasons_exist(seasons)
        if teams_in_competitions is not None:
            return self.teams.teams_in_competition_exist(teams_in_competitions)

    def _create_fixtures_table(self):
        competition_ids = self.competitions.get_competition_ids()
        fixtures_data = list()
        for id_ in competition_ids:
            if self.fixtures.load(id_).empty:
                fixture_data = self._get_fixtures_data(id_)
                fixtures_data.append(fixture_data)

        fixtures_data = pd.concat(fixtures_data).reset_index(drop=True)
        fixtures_data['id'] = fixtures_data.apply(self._create_fixture_id, axis=1)
        return fixtures_data

    def _create_players_table(self):
        unique_teams = self.teams_table['team_id'].unique()
        players_data = map(self._get_players_data, unique_teams)
        players_data = pd.concat(players_data).reset_index(drop=True)
        return players_data

    def _get_fixtures_data(self, competition_id):
        query = self.url + 'competitions/%s/fixtures' % (competition_id)
        req = requests.request('GET', query, headers=self.headers)
        print competition_id
        try:
            fixtures = pd.DataFrame(req.json()['fixtures'])
        except (KeyError, ValueError) as e:
            if 'seconds' in req.json()['error']:
                print req.json()
                print 'Number of requests exceeded, now waiting.'
                time.sleep(65)
                req = requests.request('GET', query, headers=self.headers)
                if 'error' in req.json().keys():
                    print req.json()
                    return None
            else:
                return None

            fixtures = pd.DataFrame.from_dict(req.json()['fixtures'])

        results = fixtures['result'].apply(self._dict_to_dataframe)
        odds = fixtures['odds'].apply(self._dict_to_dataframe)
        fixtures = pd.concat([fixtures, results, odds], axis=1)
        fixtures = fixtures.drop(['_links', 'result', 'odds'], axis=1)
        fixtures = fixtures.assign(competition_id=competition_id)
        ranks = fixtures.apply(self._get_ranks_row, axis=1)
        fixtures = pd.concat([fixtures, ranks], axis=1)
        fixtures['datetime'] = fixtures['date'].apply(lambda x: 
            datetime.datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ'))
        fixtures['date'] = fixtures['datetime'].dt.date
        fixtures['datetime'] = fixtures['datetime'].astype(str)
        fixtures['date'] = fixtures['date'].astype(str)
        fixtures['id'] = fixtures['homeTeamName'].astype(str) +\
            '_' + fixtures['competition_id'].astype(str) + '_' +\
            fixtures['matchday'].astype(str)
        print fixtures.head()
        print 'Now saving'
        self.fixtures.save(fixtures)
        return fixtures

    def _get_ranks_row(self, row):
        matchday = row['matchday']
        id = row['competition_id']
        query = self.url + 'competitions/' + str(id) +\
            '/leagueTable/?matchday=' + str(matchday) 
        try:
            req = requests.request('GET', query, headers=self.headers)
            ranks = req.json()
            rank_home = [rank for rank in ranks['standing']
                         if rank['teamName'] == row['homeTeamName']][0]
            rank_away = [rank for rank in ranks['standing']
                         if rank['teamName'] == row['awayTeamName']][0]
        except ValueError:
            return None
        except KeyError:
            if 'seconds' in ranks['error']:
                print 'Number of requests exceeded, now waiting.'
                time.sleep(65)
                req = requests.request('GET', query, headers=self.headers)
                ranks = req.json()
                if 'error' in req.json().keys():
                    print req.json()
                    return None

                rank_home = [rank for rank in ranks['standing']
                             if rank['teamName'] == row['homeTeamName']][0]
                rank_away = [rank for rank in ranks['standing']
                             if rank['teamName'] == row['awayTeamName']][0]
            else:
                print ranks
                return None

        cols = ['playedGames', 'goals', 'goalsAgainst', 'points',
                'wins', 'draws', 'losses']
        rank_home = {k + '_home': v for k, v in rank_home.iteritems()
                     if k in cols}
        rank_away = {k + '_away': v for k, v in rank_away.iteritems()
                     if k in cols}
        ranks = copy.copy(rank_home)
        ranks.update(rank_away)
        return pd.Series(ranks)

    def _get_competition_data(self, season):
        query = self.url + 'competitions/?season=%s' % (season)
        req = requests.request('GET', query, headers=self.headers)
        try:
            competitions = pd.DataFrame(req.json())
        except ValueError:
            print 'Number of requests exceeded, now waiting.'
            time.sleep(65)
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
        try:
            players_json = req.json()
        except:
            print req

        try:
            players_data = pd.DataFrame(players_json['players'])
        except KeyError:
            print 'Number of requests exceeded, now waiting.'
            time.sleep(65)
            req = requests.request('GET', query, headers=self.headers)
            players_json = req.json()
            players_data = pd.DataFrame(players_json['players'])

        players_data['team_id'] = team_id
        return players_data
    
    @staticmethod
    def _create_fixture_id(row):
        return row['homeTeamName'][:3] + row['awayTeamName'][:3] + row['date'][:7]

    @staticmethod
    def _dict_to_dataframe(dict_):
        series = pd.Series(dict_)
        return series

    @staticmethod
    def _get_team_code(dict_):
        code = dict_['self']['href'].split('/')[-1]
        return code



if __name__ == '__main__':
    fb = FootballData()
    fb.extract_data()
