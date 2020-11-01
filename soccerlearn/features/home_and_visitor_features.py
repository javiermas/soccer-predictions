import pandas as pd


COLUMNS_NO_TRANSFORM = ['date', 'result', 'team_id', 'season_id', 'local_team_id', 'visitor_team_id',
                        'h2h_games_played_sum', 'h2h_draw_mean']
COLUMNS_NO_DIFFERENCE = COLUMNS_NO_TRANSFORM + ['name', 'founded', 'short_code']


def compute_home_and_visitor_features(data):
    features = data['features'].copy()
    original_columns = list(features.columns)
    features = _add_local_team_id(features, data['fixtures'])
    features = _add_visitor_team_id(features, data['fixtures'])
    columns_to_transform = [col for col in features if col not in COLUMNS_NO_TRANSFORM]
    columns_to_difference = [col for col in features if col not in COLUMNS_NO_DIFFERENCE]
    local_features = features\
        .reset_index()\
        .query("team_id == local_team_id")\
        .set_index(['local_team_id', 'date'])[columns_to_transform]\
        .add_prefix('local_')
    features_with_local = pd.merge(
        features.reset_index(level=['season_id']), # To keep season_id
        local_features,
        on=['local_team_id', 'date'],
        how='left'
    )
    visitor_features = features\
        .reset_index()\
        .query("team_id == visitor_team_id")\
        .set_index(['visitor_team_id', 'date'])[columns_to_transform]\
        .add_prefix('visitor_')
    features = pd.merge(
        features_with_local,
        visitor_features,
        on=['visitor_team_id', 'date'],
        how='left'        
    )
    columns_to_drop = [col for col in original_columns if col not in COLUMNS_NO_TRANSFORM]
    features = _remove_columns(features, columns_to_drop)
    features = features.groupby(['local_team_id', 'date']).first()
    features = add_difference_features(features, columns_to_difference)
    return features


def add_difference_features(df, feature_names):
    for name in feature_names:
        df[f'difference_in_{name}'] = df[f'local_{name}'] - df[f'visitor_{name}']

    return df


def _remove_columns(df, columns_to_drop):
    return df.drop(columns=columns_to_drop)


def _add_local_team_id(features, fixtures):
    features = features.join(_get_local_team_id(fixtures), how='outer')
    assert features['local_team_id'].isnull().sum() == 0
    return features


def _add_visitor_team_id(features, fixtures):
    features = features.join(_get_visitor_team_id(fixtures), how='outer')
    assert features['visitor_team_id'].isnull().sum() == 0
    return features


def _get_local_team_id(fixtures):
    local_team_id = fixtures.reset_index().apply(lambda x: x['team_id'] if x['local'] else x['opposite_team_id'], axis=1)
    local_team_id = pd.DataFrame({
        'local_team_id': local_team_id.tolist(),
    }, index=fixtures.index)
    return local_team_id


def _get_visitor_team_id(fixtures):
    visitor_team_id = fixtures.reset_index().apply(lambda x: x['team_id'] if not x['local'] else x['opposite_team_id'], axis=1)
    visitor_team_id = pd.DataFrame({
        'visitor_team_id': visitor_team_id.tolist(),
    }, index=fixtures.index)
    return visitor_team_id
