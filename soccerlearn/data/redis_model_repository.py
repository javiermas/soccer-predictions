from redis import Redis


class NoModelInMemoryError(Exception):
    pass


class RedisModelRepository:

    def __init__(self):
        self.redis = Redis()

    def get_model(self):
        model = self.redis.get('model')
        if not model:
            raise NoModelInMemoryError('No model found in redis db')

        return model

    def set_model(self, model):
        self.redis.set('model', model)

