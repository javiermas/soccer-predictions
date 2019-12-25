import pandas as pd
import numpy as np


def get_single_result(x):
    if x['winner_team_id'] == x.name[0]:
        return 'win'
    elif not np.isnan(x['winner_team_id']):
        return 'loss'
    elif np.isnan(x['winner_team_id']) and (eval(x['scores'])['ft_score'] is not None):
        return 'draw'

def get_results(data):
    fixtures = data['pivot_fixtures_by_team']
    results = fixtures.apply(get_single_result, axis=1).rename('result')
    results_dummies = pd.get_dummies(results)
    results_num = results.map({'win': 0, 'draw': 1, 'loss': 2}).rename('result_num')
    return pd.concat([results, results_num, results_dummies], axis=1)


def get_games_played(data):
    fixtures = data['pivot_fixtures_by_team'].copy()
    fixtures = fixtures.sort_index()
    fixtures['count'] = 1
    games_played = fixtures.groupby(['team_id'])[['count']].cumsum()
    return games_played


def get_games_played_current_season(data):
    fixtures = data['pivot_fixtures_by_team'].copy()
    fixtures = fixtures.sort_index()
    fixtures['count'] = 1
    games_played = fixtures.groupby(['team_id', 'season_id'])[['count']].cumsum()\
        .rename(columns={'count': 'games_played_current_season'})
    return games_played


def get_cumulative_results(data):
    fixtures = data['get_results'].copy()
    fixtures = fixtures.join(data['pivot_fixtures_by_team'][['season_id']])
    fixtures = fixtures.sort_index()
    cumulative_results = fixtures.groupby(['team_id'])['win', 'draw'].cumsum()\
        .rename(columns={'win': 'games_won_all_time', 'draw': 'games_drew_all_time'})
    return cumulative_results


def get_cumulative_results_current_season(data):
    fixtures = data['get_results'].copy()
    fixtures = fixtures.join(data['pivot_fixtures_by_team'][['season_id']])
    fixtures = fixtures.sort_index()
    cumulative_results = fixtures.groupby(['team_id', 'season_id'])['win', 'draw'].cumsum()\
        .rename(columns={'win': 'games_won_current_season',
                         'draw': 'games_drew_current_season'})
    return cumulative_results
