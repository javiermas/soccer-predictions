import pandas as pd


class LocalRepository:

    def __init__(self, path='./data', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path


class RawDataRepository:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.standings_filename = 'standings'
        self.seasons_filename = 'seasons'
        self.teams_filename = 'teams_league'
        self.fixtures_filename = 'fixtures_and_odds'