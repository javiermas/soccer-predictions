import os
import requests
import pandas as pd
import numpy as np


class FootballData(object):
    '''
    Class FootballData. Provides a connection to the
    football-data API.

    Requires to set the football-api key as an environmental
    variable.
    '''

    def __init__(self):
        self.url = 'http://api.football-data.org/v1/'
        self.headers = {'X-Auth-Token': os.environ['FOOTBALL_API_KEY']}
        self.path = os.getcwd().split('soccer_predictions')[0] + \
            'soccer_predictions/'
        self.competitions_table = self._load_competitions_table()
        self.teams_table = self._load_teams_table()
        self.players_table = self._load_players_table()

    def get_competition_fixtures(self, competition, season):
        '''Receives a competition id and a season and
        returns a dataframe with the corresponding
        fixtures.
        '''
        if isinstance(season, str):
            season = int(season)

        competition_id = np.unique(self.competitions_table.loc[
            (self.competitions_table['competition'] == competition) &
            (self.competitions_table['season'] == season), 'id'])[0]
        query = self.url + 'competitions/%s/fixtures' % competition_id
        req = requests.request('GET', query, headers=self.headers)
        comp_json = req.json()
        competition_fixtures = pd.DataFrame.from_dict(comp_json['fixtures'])
        results = (competition_fixtures['result'])
        results = results.apply(self._dict_to_dataframe)
        competition_fixtures = pd.concat(
            (competition_fixtures, results), axis=1)
        competition_fixtures = competition_fixtures.drop('result', axis=1)
        return competition_fixtures

    def _load_competitions_table(self):
        try:
            competitions_table = pd.read_csv(self.path +
                                             'data/competitions_table.csv')
        except IOError:
            competitions_table = self._create_competitions_table()
            competitions_table.to_csv(self.path +
                                      'data/competitions_table.csv',
                                      index=False,
                                      encoding='utf-8')
        return competitions_table

    def _load_teams_table(self):
        try:
            teams_table = pd.read_csv(self.path + 'data/teams_table.csv')
        except IOError:
            teams_table = self._create_teams_table()
            teams_table.to_csv(self.path + 'data/teams_table.csv',
                               index=False,
                               encoding='utf-8')

        return teams_table

    def _load_players_table(self):
        try:
            players_table = pd.read_csv(self.path + 'data/players_table.csv')
        except IOError:
            players_table = self._create_teams_table()
            players_table.to_csv(self.path + 'data/players_table.csv',
                                 index=False,
                                 encoding='utf-8')

        return players_table

    def _create_competitions_table(self):
        seasons = ['2015', '2016', '2017']
        competitions_data = map(self._get_competition_data, seasons)
        competitions_data = pd.concat(competitions_data).reset_index(drop=True)
        '''
            for c in competitions:
                ids.append(c['id'])
                leagues.append(c['league'])
                league_names.append(c['caption'])
                seasons.append(c['year'])

        competitions_table = pd.DataFrame({
            'id': ids,
            'competition': leagues,
            'competition_name': league_names,
            'season': seasons
        })
        '''
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
        competitions = pd.DataFrame(req.json())
        competitions['season'] = season
        return competitions

    def _get_team_data(self, competition_id):
        '''
        cols_to_keep = ['code', 'name', 'shortName',
                        'squadMarketValue', '_links']
        '''
        query = self.url + 'competitions/%s/teams' % competition_id
        req = requests.request('GET', query, headers=self.headers)
        teams_json = req.json()
        if teams_json.keys()[0] == 'error':
            return None

        data_teams = pd.DataFrame(teams_json['teams'])  # [cols_to_keep]
        data_teams['team_id'] = data_teams['_links']\
            .apply(self._get_team_code)
        data_teams['competition_id'] = competition_id
        # data_teams = data_teams.drop('_links', axis=1)
        return data_teams

    def _get_players_data(self, team_id):
        query = self.url + 'teams/%s/players' % team_id
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
