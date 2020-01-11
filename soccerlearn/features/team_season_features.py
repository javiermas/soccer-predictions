import pandas as pd

def _amounts_to_float(amount):
    if amount is None:
        return amount
    elif 'M' in amount:
        return float(amount.split('M')[0]) * 1e6
    elif 'K' in amount:
        return float(amount.split('K')[0]) * 1e3

def _get_amount_transferred_single_team(transfer_data):
    transfers = pd.DataFrame(transfer_data).dropna(subset=['season_id'])
    transfers['season_id'] = transfers['season_id'].astype(int)
    transfers['amount_num'] = transfers['amount'].apply(_amounts_to_float)
    return transfers

def get_amount_transferred(data):
    team_data = data['teams']
    transfer_data = []
    for index, row in team_data.iterrows():
        transfer_data.append(_get_amount_transferred_single_team(eval(row['transfers'])))

    transfer_data = pd.concat(transfer_data).reset_index(drop=True)
    transfer_data = transfer_data\
        .groupby(['from_team_id', 'season_id', 'type'])[['amount_num']]\
        .sum().reset_index()
    transfer_data['team_season'] = transfer_data['from_team_id'].astype(str) + '_'\
        + transfer_data['season_id'].astype(str)
    transfer_data = transfer_data.pivot(
        index='team_season',
        columns='type',
        values='amount_num'
    )
    transfer_data = transfer_data.reset_index()\
        .rename(columns={'IN': 'amount_transferred_in', 'OUT': 'amount_transferred_out'})
    transfer_data['team_id'] = transfer_data['team_season']\
        .apply(lambda x: x.split('_')[0]).astype(int)
    transfer_data['season_id'] = transfer_data['team_season']\
        .apply(lambda x: x.split('_')[1]).astype(int)
    return transfer_data.drop(columns='team_season').set_index(['team_id', 'season_id'])
