import pandas as pd


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


def get_amount_transferred(data):
    team_data = data['teams']
    transfer_data = []
    for index, row in team_data.iterrows():
        transfer_data.append(_get_amount_transferred_single_team(eval(row['transfers'])))

    transfer_data = pd.concat(transfer_data).reset_index(drop=True)
    transfer_data = transfer_data\
        .groupby(['from_team_id', 'season_id', 'type'])[['amount_num']]\
        .sum().reset_index()
    transfer_data['team_season'] = transfer_data['from_team_id'].astype(str) + '_'\
        + transfer_data['season_id'].astype(str)
    transfer_data = transfer_data.pivot(
        index='team_season',
        columns='type',
        values='amount_num'
    )
    transfer_data = transfer_data.reset_index()\
        .rename(columns={'IN': 'amount_transferred_in', 'OUT': 'amount_transferred_out'})
    transfer_data['amount_transferred'] = transfer_data['amount_transferred_in']\
        + transfer_data['amount_transferred_out']
    transfer_data['team_id'] = transfer_data['team_season']\
        .apply(lambda x: x.split('_')[0]).astype(int)
    transfer_data['season_id'] = transfer_data['team_season']\
        .apply(lambda x: x.split('_')[1]).astype(int)
    return transfer_data.drop(columns='team_season').set_index(['team_id', 'season_id'])


def _amounts_to_float(amount):
    if amount is None:
        return amount
    elif 'M' in amount:
        return float(amount.split('M')[0]) * 1e6
    elif 'K' in amount:
        return float(amount.split('K')[0]) * 1e3


def _get_amount_transferred_single_team(transfer_data):
    transfers = pd.DataFrame(transfer_data).dropna(subset=['season_id'])
    transfers['season_id'] = transfers['season_id'].astype(int)
    transfers['amount_num'] = transfers['amount'].apply(_amounts_to_float)
    return transfers


def compute_previous_season_features(data, lags=[1]):
    fixture_features = data['fixture_features'].copy().reset_index()
    feature_names = ['goals_scored_current_season',
                     'points_current_season', 'goals_conceded_current_season']
    # Here we are losing the last game
    features_per_season = fixture_features.groupby(['team_id', 'season_id'])[feature_names].max()
    features_per_season = features_per_season.join(data['positions'], how='left')
    #features_per_season = fixture_features\
    #    .groupby(['season_id', 'team_id'])[feature_names].max().reset_index()\
    #    .sort_values(['team_id', 'season_start_year'])\
    #    .rename(columns={c: c.replace('current_season', 'end_season') for c in feature_names})
    previous_season_features = []
    for lag in lags:
        lagged_features = features_per_season.groupby('team_id').shift(lag)
        lagged_features.columns = [f'{c}_lag_{lag}' for c in lagged_features.columns]
        previous_season_features.append(lagged_features)

    previous_season_features = pd.concat(previous_season_features, axis=1)
    return previous_season_features
