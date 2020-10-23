import pandas as pd


def compute_home_and_visitor_features(data, columns_with_no_transform=['date']):
    features = data['features'].copy()
    original_columns = list(features.columns)
    features = _add_local_team_id(features, data['fixtures'])
    features = _add_visitor_team_id(features, data['fixtures'])
    renaming_dict = {f'local_{c}': c for c in columns_with_no_transform}
    local_features = features.reset_index().add_prefix('local_').rename(columns=renaming_dict)
    features_with_local = pd.merge(
        features,
        local_features,
        on=['local_team_id', 'date'],
        how='left'
    )
    renaming_dict = {f'visitor_{c}': c for c in columns_with_no_transform}        
    visitor_features = features.reset_index().add_prefix('visitor_').rename(columns=renaming_dict)
    features = pd.merge(
        features_with_local,
        visitor_features,
        on=['visitor_team_id', 'date'],
        how='left'        
    )
    features = _remove_columns(features, original_columns)
    return features.groupby(['local_team_id', 'date']).first()


def _remove_columns(df, columns_to_drop):
    columns_to_drop += [f'{x}_{y}_team_id' for x, y in [('local', 'visitor'), ('visitor', 'local'), ('local', 'local'), ('visitor', 'visitor')]]
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