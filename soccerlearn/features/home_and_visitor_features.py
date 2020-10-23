import pandas as pd


def compute_home_and_visitor_features(data):
    features = data['features'].copy()
    features = _add_local_team_id(features, data['fixtures'])
    features = _add_visitor_team_id(features, data['fixtures'])
    local_features = features.add_prefix('local_')\
        .rename(columns={
            'local_local_team_id': 'local_team_id',
        })
    features = pd.merge(
        features,
        local_features,
        on=['local_team_id', 'date'],
    )
    visitor_features = features.add_prefix('visitor_')\
        .rename(columns={
            'visitor_visitor_team_id': 'visitor_team_id',
        })
    features = pd.merge(
        features,
        visitor_features,
        on=['visitor_team_id', 'date']
    )
    return features


def _add_local_team_id(features, fixtures):
    features['local_team_id'] = _get_local_team_id(fixtures)
    assert features['local_team_id'].isnull().sum() == 0
    return features


def _add_visitor_team_id(features, fixtures):
    features['visitor_team_id'] = _get_visitor_team_id(fixtures)
    assert features['visitor_team_id'].isnull().sum() == 0
    return features


def _get_local_team_id(fixtures):
    local_team_id = fixtures.reset_index().apply(lambda x: x['team_id'] if x['local'] else x['opposite_team_id'], axis=1)
    local_team_id = pd.DataFrame({
        'local_team_id': local_team_id.tolist(),
    }, index=fixtures.index)
    return local_team_id['local_team_id']

def _get_visitor_team_id(fixtures):
    visitor_team_id = fixtures.reset_index().apply(lambda x: x['team_id'] if not x['local'] else x['opposite_team_id'], axis=1)
    visitor_team_id = pd.DataFrame({
        'visitor_team_id': visitor_team_id.tolist(),
    }, index=fixtures.index)
    return visitor_team_id['visitor_team_id']