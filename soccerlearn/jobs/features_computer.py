from soccerlearn import get_logger


class FeaturesComputer:

    def __init__(self, pipeline, raw_data_repository, features_repository, *args, **kwargs):
        self.pipeline = pipeline
        self.logger = get_logger('airflow.task')
        self.raw_data_repository = raw_data_repository
        self.features_repository = features_repository
        self.run_parameters = {}
        self.logger = get_logger(self.__class__.__name__)

    def __call__(self, league, start_date, end_date, *args, **kwargs):
        self.run(league, start_date, end_date)

    def run(self, league, start_date, end_date):
        self.set_run_parameters(league, start_date, end_date)
        self.logger.info('Reading data...')
        data = self.read_data()
        self.logger.info('Data read\n Computing features...')
        data = self.transform_data(data)
        self.logger.info('Features computed\n Storing features...')
        self.store_data(data)
        self.logger.info('Features stored\n FeaturesComputer finished successfully')

    def set_run_parameters(self, league, start_date, end_date):
        self.run_parameters = {
            'league': league,
            'start_date': start_date,
            'end_date': end_date,
        }
        self.run_parameters['identifier'] = (
            f'{self.__class__.__name__}'
            f'_{"_".join(self.run_parameters.values())}'
        )

    def read_data(self):
        return self.raw_data_repository.read_data(
            self.run_parameters['league'],
            self.run_parameters['start_date'],
            self.run_parameters['end_date']
        )

    def transform_data(self, data):
        return self.pipeline(data)

    def store_data(self, data):
        self.features_repository.store_features(data, self.run_parameters['identifier'])
