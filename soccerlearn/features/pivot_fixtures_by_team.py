import pandas as pd


def pivot_fixtures_by_team(data):
    fixtures = data['fixtures']
    odd_vars = [col for col in fixtures if 'odd' in col]
    cols_to_keep = ['round_id', 'date', 'scores', 'winner_team_id',
                    'season_id', 'season_start_year']
    features = pd.melt(
        fixtures,
        id_vars=cols_to_keep+ odd_vars,
        value_vars=['localteam_id', 'visitorteam_id'],
        value_name='team_id'
    )
    features['local'] = features['variable'].apply(lambda x: x == 'localteam_id')
    features = features.drop(columns='variable')
    return features.set_index(['team_id', 'date'])
