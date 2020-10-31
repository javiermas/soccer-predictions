from soccerlearn import get_logger


class DataExtractor:

    def __init__(self, data_config):
        self.data = data_config
        self.logger = get_logger('airflow.task')

    def __call__(self, task_instance, *args, **kwargs):
        self.logger.info(kwargs)
        #task_instance = context['task_instance']
        task_instance.xcom_push('some_key', 'papi')
        return self.run()

    def run(self):
        print('running')
        return 'running'

    def push_function(self):
        return 'hi'
