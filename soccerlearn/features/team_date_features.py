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
    fixtures = data['pivot_fixtures_by_team'].copy()
    results = fixtures.apply(get_single_result, axis=1).rename('result')
    results_dummies = pd.get_dummies(results)
    results_num = results.map({'win': 0, 'draw': 1, 'loss': 2}).rename('result_num')
    return pd.concat([results, results_num, results_dummies], axis=1)


def get_winning_odds(data):
    fixtures = data['pivot_fixtures_by_team'].copy()
    winning_odds = pd.DataFrame(
        fixtures.apply(lambda x: x['odd_value_1'] if x['local'] else x['odd_value_2'], axis=1),
        columns=['winning_odds'],
    )
    return winning_odds


def get_scores(data):
    fixtures = data['pivot_fixtures_by_team'].copy()
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
    fixtures = data['pivot_fixtures_by_team'].copy()
    fixtures = fixtures.sort_index()
    fixtures['count'] = 1
    games_played = fixtures.groupby(['team_id'])[['count']].cumsum()\
        .rename(columns={'count': 'games_played_all_time'})
    return games_played


def get_games_played_current_season(data):
    fixtures = data['pivot_fixtures_by_team'].copy()
    fixtures = fixtures.sort_index()
    fixtures['count'] = 1
    games_played = fixtures.groupby(['team_id', 'season_id'])[['count']]\
        .shift(1)\
        .cumsum()\
        .rename(columns={'count': 'games_played_current_season'})\
        .fillna(0)
    return games_played


def get_cumulative_results(data):
    fixtures = data['get_results'].copy()
    fixtures = fixtures\
        .join(data['pivot_fixtures_by_team'][['season_id']])\
        .join(data['get_scores'])
    fixtures = fixtures.sort_index()
    columns_to_cumulate = ['win', 'draw', 'goals_scored', 'goals_conceded']
    cumulative_results = fixtures.groupby(['team_id'])[columns_to_cumulate]\
        .shift(1)\
        .cumsum()\
        .fillna(0)\
        .rename(columns={col: f'{col}_all_time' for col in columns_to_cumulate})
    return cumulative_results


def get_cumulative_results_current_season(data):
    fixtures = data['get_results'].copy()
    fixtures = fixtures\
        .join(data['pivot_fixtures_by_team'][['season_id']])\
        .join(data['get_scores'])
    fixtures = fixtures.sort_index().reset_index()
    columns_to_shift = ['win', 'draw', 'goals_scored', 'goals_conceded']
    for column in columns_to_shift:
        fixtures[f'{column}_lag_1'] = fixtures.groupby(['team_id', 'season_id'])[column].shift()

    columns_to_cumulate = [f'{column}_lag_1' for column in columns_to_shift]
    renaming_dict = {col: f'{col.split("_lag_1")[0]}_current_season'
                     for col in columns_to_cumulate}
    cumulative_results = fixtures.reset_index()\
        .groupby(['team_id', 'season_id'])[columns_to_cumulate]\
        .cumsum()\
        .fillna(0)\
        .rename(columns=renaming_dict)
    cumulative_results['team_id'] = fixtures['team_id']
    cumulative_results['date'] = fixtures['date']
    cumulative_results['points_current_season'] = cumulative_results['win_current_season']*3\
        + cumulative_results['draw_current_season']
    return cumulative_results.set_index(['team_id', 'date'])


def get_rolling_results(data):
    PERIODS = 5
    results = data['get_results'].sort_index().copy()
    results['points_won'] = results['win'] * 3 + results['draw']
    results[f'points_won_last_{PERIODS}_games_sum'] = results\
        .groupby('team_id')['points_won']\
        .shift(1)\
        .rolling(PERIODS).sum()
    
    return results[[f'points_won_last_{PERIODS}_games_sum']]
