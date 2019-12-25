import pandas as pd


def unpivot_fixtures_by_odds(data):
    fixtures = data['fixtures']
    fixtures_unpivoted = fixtures.dropna(subset=['odd_value']).pivot(index='id', columns='odd_name', values=['odd_value', 'odd_winning']).astype(float)
    fixtures_unpivoted.columns = ['_'.join(c) for c in fixtures_unpivoted.columns]
    fixtures_without_odds = fixtures.drop_duplicates(subset=['id']).drop(columns=['odd_value', 'odd_winning', 'odd_name'])
    fixtures_unpivoted = pd.merge(fixtures_without_odds, fixtures_unpivoted, on='id', how='left') 
    return fixtures_unpivoted
