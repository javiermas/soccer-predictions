import pandas as pd


def unpivot_fixtures_by_odds(data, multiple_bookmakers=True):
    fixtures = data['fixtures']
    if multiple_bookmakers:
        fixtures['odd_name_bookmaker'] = fixtures.apply(
            lambda x: f'{x.odd_name}_{x.bookmaker_name}'
            if not pd.isnull(x['bookmaker_name']) else None, axis=1
        )
        fixtures_unpivoted = fixtures.dropna(subset=['odd_value'])\
            .pivot(index='id', columns='odd_name_bookmaker',
                   values=['odd_value', 'odd_winning'])\
            .astype(float)
        fixtures_unpivoted.columns = ['_'.join(c) for c in fixtures_unpivoted.columns]
    else:
        fixtures_unpivoted = fixtures.dropna(subset=['odd_value'])\
            .pivot(index='id', columns='odd_name',
                   values=['odd_value', 'odd_winning'])\
            .astype(float)
        fixtures_unpivoted.columns = ['_'.join(c) for c in fixtures_unpivoted.columns]

    fixtures_without_odds = fixtures.drop_duplicates(subset=['id']).drop(columns=['odd_value', 'odd_winning', 'odd_name'])
    fixtures_unpivoted = pd.merge(fixtures_without_odds, fixtures_unpivoted, on='id', how='left') 
    data['fixtures'] = fixtures_unpivoted
    return data
