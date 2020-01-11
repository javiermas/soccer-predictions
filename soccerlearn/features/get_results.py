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
    games_played = fixtures.groupby(['team_id', 'season_id'])[['count']].cumsum()\
        .rename(columns={'count': 'games_played_current_season'})
    return games_played


def get_cumulative_results(data):
    fixtures = data['get_results'].copy()
    fixtures = fixtures\
        .join(data['pivot_fixtures_by_team'][['season_id']])\
        .join(data['get_scores'])
    fixtures = fixtures.sort_index()
    columns_to_cumulate = ['win', 'draw', 'goals_scored', 'goals_conceded']
    cumulative_results = fixtures.groupby(['team_id'])[columns_to_cumulate].cumsum()\
        .rename(columns={col: f'{col}_all_time' for col in columns_to_cumulate})
    return cumulative_results


def get_cumulative_results_current_season(data):
    fixtures = data['get_results'].copy()
    fixtures = fixtures\
        .join(data['pivot_fixtures_by_team'][['season_id']])\
        .join(data['get_scores'])
    fixtures = fixtures.sort_index()
    columns_to_cumulate = ['win', 'draw', 'goals_scored', 'goals_conceded']
    cumulative_results = fixtures.groupby(['team_id', 'season_id'])[columns_to_cumulate]\
        .cumsum()\
        .rename(columns={col: f'{col}_current_season' for col in columns_to_cumulate})
    cumulative_results['points_current_season'] = cumulative_results['win_current_season']*3\
        + cumulative_results['draw_current_season']
    return cumulative_results


def compute_position_end_season(data):
    standings = data['standings']
    standing_features = []
    for i, elem in standings.iterrows():
        for team in eval(elem['standings']):
            standing_features.append({
                'team_id': team['team_id'],
                'season_id': elem['season_id'],
                'position_end_season': team['position'],
            })

    standing_features = pd.DataFrame(standing_features).set_index(['team_id', 'season_id'])
    return standing_features


def compute_previous_season_features(data, lags=[1]):
    fixture_features = data['fixture_features']
    feature_names = ['position_end_season', 'goals_scored_current_season',
                    'points_current_season', 'goals_conceded_current_season']
    features_per_season = fixture_features\
        .groupby(['season_start_year', 'team_id'])[feature_names].max().sort_index()\
        .rename(columns={c: c.replace('current_season', 'end_season') for c in feature_names})

    previous_season_features = []
    for lag in lags:
        lagged_features = features_per_season.groupby('team_id').shift(lag)
        lagged_features.columns = [f'{c}_lag_{lag}' for c in lagged_features.columns]
        previous_season_features.append(lagged_features)

    previous_season_features = pd.concat(previous_season_features, axis=1)
    return previous_season_features
