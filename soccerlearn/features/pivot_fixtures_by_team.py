import pandas as pd


def pivot_fixtures_by_team(data):
    fixtures = data['fixtures']
    odd_vars = [col for col in fixtures if 'odd' in col]
    cols_to_keep = ['round_id', 'date', 'scores', 'winner_team_id',
                    'season_id', 'season_start_year', 'h2h_id']
    features = pd.melt(
        fixtures,
        id_vars=cols_to_keep+ odd_vars,
        value_vars=['localteam_id', 'visitorteam_id'],
        value_name='team_id'
    )
    features['local'] = features['variable'].apply(lambda x: x == 'localteam_id')
    features['opposite_team_id'] = features.apply(
        lambda x: int([v for v in x['h2h_id'].split('_') if v != str(x['team_id'])][0]), axis=1
    )
    features = features.drop(columns='variable')
    data['fixtures'] = features.set_index(['team_id', 'date', 'season_id'])
    return data
