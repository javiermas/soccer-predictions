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
    fixtures = data['fixtures'].copy()
    results = fixtures.apply(get_single_result, axis=1).rename('result')
    results_dummies = pd.get_dummies(results)
    results_num = results.rename('result_num')#.map({'win': 0, 'draw': 1, 'loss': 2}).rename('result_num')
    return pd.concat([results, results_num, results_dummies], axis=1)
 

def get_winning_odds(data):
    fixtures = data['fixtures'].copy()
    winning_odds = pd.DataFrame(
        fixtures.apply(lambda x: x['odd_value_1'] if x['local'] else x['odd_value_2'], axis=1),
        columns=['winning_odds'],
    )
    return winning_odds


def get_scores(data):
    fixtures = data['fixtures'].copy()
    fixtures['goals_scored'] = fixtures.apply(
        lambda x: eval(x['scores'])['localteam_score']
        if x['local'] else eval(x['scores'])['visitorteam_score'],
        axis=1
    )
    fixtures['goals_conceded'] = fixtures.apply(
        lambda x: eval(x['scores'])['visitorteam_score']
        if x['local'] else eval(x['scores'])['localteam_score'],
        axis=1
    )
    return fixtures[['goals_scored', 'goals_conceded']]


def get_games_played(data):
    fixtures = data['fixtures'].copy()
    fixtures = fixtures.sort_index()
    fixtures['count'] = 1
    games_played = fixtures.groupby(['team_id'])[['count']].cumsum()\
        .rename(columns={'count': 'games_played_all_time'})
    return games_played


def get_games_played_current_season(data):
    fixtures = data['fixtures'].copy()
    fixtures['count'] = 1
    games_played = fixtures.groupby(['team_id', 'season_id'])[['count']]\
        .shift(1)\
        .cumsum()\
        .rename(columns={'count': 'games_played_current_season'})\
        .fillna(0)
    return games_played


def get_cumulative_results(data):
    fixtures = data['fixtures'].copy()
    cumulative_results = fixtures.groupby(['team_id'])[columns_to_cumulate]\
        .shift(1)\
        .cumsum()\
        .fillna(0)\
        .rename(columns={col: f'{col}_all_time' for col in columns_to_cumulate})
    return cumulative_results

def get_cumulative_results_current_season(data):
    fixtures = data['fixtures'].copy()
    fixtures['games_played'] = 1
    columns_to_shift = ['win', 'draw', 'goals_scored', 'goals_conceded', 'games_played']
    for column in columns_to_shift:
        fixtures[f'{column}_lag_1'] = fixtures.groupby(['team_id', 'season_id'])[column].shift()

    columns_to_cumulate = [f'{column}_lag_1' for column in columns_to_shift]
    renaming_dict = {col: f'{col.split("_lag_1")[0]}_current_season'
                     for col in columns_to_cumulate}
    cumulative_results = fixtures\
        .groupby(['team_id', 'season_id'])[columns_to_cumulate]\
        .cumsum()\
        .fillna(0)\
        .rename(columns=renaming_dict)
    cumulative_results['points_current_season'] = cumulative_results['win_current_season']*3\
        + cumulative_results['draw_current_season']
    return cumulative_results


def get_h2h_features(data):
    fixtures = data['fixtures'].copy()
    fixtures['games_played'] = 1
    columns_mean = ['win', 'draw', 'goals_scored', 'goals_conceded']
    columns_sum = ['games_played']
    fixtures_shifted = fixtures\
        .reset_index()\
        .set_index(['h2h_id', 'team_id', 'date'])\
	    .groupby(['team_id', 'h2h_id'])[columns_mean + columns_sum]\
        .shift(1)\
        .reset_index()

    h2h_features_mean = fixtures_shifted\
        .set_index('date')\
        .groupby(['team_id', 'h2h_id'])[columns_mean]\
        .rolling(100, min_periods=1).mean()\
        .rename(columns={col: f'h2h_{col}_mean' for col in columns_mean})\
    
    h2h_features_sum = fixtures_shifted\
        .set_index(['team_id', 'h2h_id', 'date'])\
        .fillna(0)\
        .groupby(['team_id', 'h2h_id'])[columns_sum]\
        .cumsum()\
        .rename(columns={col: f'h2h_{col}_sum' for col in columns_sum})
    h2h_features = h2h_features_mean.join(h2h_features_sum)
    return h2h_features.reset_index(level='h2h_id', drop=True)


def get_rolling_results(data, periods=5, agg_func='mean'):
    fixtures = data['fixtures'].copy()
    fixtures['points'] = fixtures['win'] * 3 + fixtures['draw']
    columns_to_shift = ['win', 'draw', 'goals_scored', 'goals_conceded', 'points']
    for column in columns_to_shift:
        fixtures[f'{column}_lag_1'] = fixtures.groupby(['team_id', 'season_id'])[column].shift()

    columns_to_cumulate = [f'{column}_lag_1' for column in columns_to_shift]
    renaming_dict = {col: f'{col.split("_lag_1")[0]}_rolling_{periods}_{agg_func}'
                     for col in columns_to_cumulate}
    if agg_func == 'ewm':
        rolling_results = []
        for column in columns_to_cumulate:
            rolling_results.append(
                fixtures.reset_index(level='season_id')\
                    .groupby(['team_id'])[column]\
                    .apply(lambda g: g.ewm(span=periods, min_periods=1).mean())
            )
        rolling_results = pd.concat(rolling_results, axis=1)\
            .rename(columns=renaming_dict)
    else:
        agg_func = dict.fromkeys(renaming_dict, agg_func)
        rolling_results = fixtures.reset_index()\
            .groupby(['team_id'])\
            .rolling(periods, min_periods=1, on='date')\
            .agg(agg_func)\
            .rename(columns=renaming_dict)

    return rolling_results


def extract_results(data):
    fixtures = data['fixtures']\
        .join(get_scores(data))\
        .join(get_results(data))
    data['fixtures'] = fixtures.sort_index()
    return data


def compute_target(data):
    return data['fixtures'][['result']]