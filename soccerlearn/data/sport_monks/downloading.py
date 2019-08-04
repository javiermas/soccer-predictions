import pandas as pd
from datetime import datetime, date
import requests
from sportmonks.soccer import SoccerApiV2


MARKET_ID = 80


def load_leagues(path='data/leagues.csv'):
    return pd.read_csv(path)


def load_bookmakers(path='data/bookmakers.csv'):
    return pd.read_csv(path)


def get_league_id_from_name(league_data, league_name):
    return league_data.loc[league_data['name'] == league_name, 'id'].iloc[0]


def get_bet365_id(bookmaker_data):
    return bookmaker_data.loc[bookmaker_data['name'] == 'bet365', 'id'].iloc[0]


def download_leagues(token, path='data/leagues.csv'):
    api = SoccerApiV2(api_token=token)
    leagues = api.leagues(includes=['country', 'seasons'])
    leagues = pd.DataFrame(leagues)
    leagues['country_name'] = leagues['country'].apply(lambda x: x['name'])
    leagues['country_id'] = leagues['country'].apply(lambda x: x['id'])
    leagues.to_csv(path, index=False)

    
def download_bookmakers(token, path='data/bookmakers.csv'):
    api = SoccerApiV2(api_token=token)
    bookmakers = api.bookmakers()
    bookmakers = pd.DataFrame(bookmakers)
    bookmakers.to_csv(path, index=False)

def download_fixtures_and_odds_single_league(token, league_name, start_date, end_date, path=None):
    league_data = load_leagues()
    league_id = get_league_id_from_name(league_data, league_name)
    
    api = SoccerApiV2(api_token=token)
    fixture_data = api.fixtures(start_date, end_date, league_ids=[league_id], includes=['flatOdds'])
    fixture_data = pd.DataFrame(fixture_data)
    odds = []
    bookmaker_data = load_bookmakers()
    bookmaker_id = get_bet365_id(bookmaker_data)
    for index, row in fixture_data.iterrows():
        try:
            single_odd_data = [o['odds'] for o in row['flatOdds'] if (o['bookmaker_id'] == bookmaker_id) and (o['market_id'] == MARKET_ID)][0]
        except IndexError: # No odd data 
            continue
        odds.extend([{'odd_name': o['label'], 'odd_value': o['value'], 'odd_winning': o['winning'], 'id': row['id']} for o in single_odd_data])

    odds = pd.DataFrame(odds)
    fixture_and_odds = pd.merge(fixture_data, odds, on='id', how='left')
    if path is None:
        path = f'data/fixtures_and_odds_{league_name}_{str(start_date)}_{str(end_date)}.csv'
     
    fixture_and_odds.to_csv(path)
    print(f'Saved fixtures and odds for league {league_name}!')

