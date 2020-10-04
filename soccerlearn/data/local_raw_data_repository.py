import os
import pandas as pd

from soccerlearn.data.base import LocalRepository, RawDataRepository


class LocalRawDataRepository(LocalRepository, RawDataRepository):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read_data(self, league, start_date, end_date):
        data = {
            'standings': pd.read_csv(f'{self.path}/{self.standings_filename}_{league}.csv'),
            'seasons': pd.read_csv(f'{self.path}/{self.seasons_filename}.csv'),
            'teams': pd.read_csv(f'{self.path}/{self.teams_filename}_{league}.csv'),
            'fixtures': pd.read_csv(
                f'{self.path}/{self.fixtures_filename}_{league}_{start_date}_{end_date}.csv'
            ),
        }
        return data
