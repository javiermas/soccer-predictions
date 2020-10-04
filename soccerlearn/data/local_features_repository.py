from soccerlearn.data.base import LocalRepository


class LocalFeaturesRepository(LocalRepository):

    def store_features(self, data, identifier):
        data.to_csv(f'{self.path}/{identifier}.csv')