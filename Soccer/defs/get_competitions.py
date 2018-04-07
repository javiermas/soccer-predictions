import requests
import pandas as pd


def get_competitions(create=True, save=False):
    if not create:
        return pd.DataFrame.from_csv('competition_ids')

   query_string = 'http://api.football-data.org/v1/competitions/?season='
    ids, leagues, league_names, years = [[] for i in range(4)]
    for year in ['2015', '2016', '2017']:
        req = requests.request('GET', query_string + year)
        competitions = req.json()
        for c in competitions:
            ids.append(c['id'])
            leagues.append(c['league'])
            league_names.append(c['caption'])
            years.append(c['year'])

    league_ids = pd.DataFrame({
        'Ids': ids,
        'League': leagues,
        'LeagueName': league_names,
        'Year': years
    })
    if save:
        league_ids.to_csv('competition_ids')

    return league_ids
