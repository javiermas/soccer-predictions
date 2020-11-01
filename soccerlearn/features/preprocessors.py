import pandas as pd
import numpy as np
import math


def rename_columns(data):
    data['seasons'] = data['seasons'].rename(columns={'id': 'season_id', 'name': 'season_name'})
    return data
    
def process_fixtures(data):
    fixtures_and_odds = pd.merge(data['fixtures'], data['seasons'][['season_id', 'season_name']], on='season_id', how='left')
    fixtures_and_odds['season_start_year'] = fixtures_and_odds['season_name'].apply(lambda x: x.split('/')[0])
    fixtures_and_odds['date_time'] = pd.to_datetime(fixtures_and_odds['time'].apply(lambda x: eval(x)['starting_at']['date_time']))
    fixtures_and_odds['year'] = fixtures_and_odds['date_time'].dt.year
    fixtures_and_odds['month'] = fixtures_and_odds['date_time'].dt.month
    fixtures_and_odds['date'] = pd.to_datetime(fixtures_and_odds['date_time'].dt.date)
    fixtures_and_odds['round_id'] = fixtures_and_odds['round_id'].apply(lambda x: np.nan if math.isnan(x) else str(int(x)))
    data['fixtures'] = fixtures_and_odds
    return data


def add_h2h_id_to_fixtures(data):
    data['fixtures']['h2h_id'] = data['fixtures'].apply(lambda x: '_'.join(map(str, sorted([x['localteam_id'], x['visitorteam_id']]))), axis=1)
    return data


def add_team_data_to_features(data):
    features = data['features'].copy()
    team_data = data['teams'].groupby(['id']).first().reset_index()
    features = pd.merge(
        features.reset_index(),
        team_data[['name', 'short_code', 'founded', 'id']],
        left_on='team_id',
        right_on='id',
        how='left'
    ).set_index(['team_id', 'season_id', 'date'])
    data['features'] = features
    return data