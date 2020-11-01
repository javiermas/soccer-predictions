from functools import reduce
import pandas as pd

from soccerlearn.get_logger import get_logger


class Pipeline:

    def __init__(self, transformer_funcs, keys_to_keep=None):
        self.transformer_funcs = transformer_funcs
        self.keys_to_keep = keys_to_keep
        self.logger = get_logger(self.__class__.__name__)

    def __call__(self, data, *args, **kwargs):
        return self.transform(data)

    def transform(self, data):
        for name, func, kwargs in self.transformer_funcs:
            if name:
                self.logger.info(f'Creating feature {name}')
                data[name] = func(data, **kwargs)
            else:
                self.logger.info(f'Applying modifier {func.__name__}')
                data = func(data, **kwargs)
        
        feature_names = self.get_feature_names()
        data = self.combine_dataframes([data[k] for k in feature_names])
        print('Pipeline finished')
        return data.sort_index()

    def get_feature_names(self):
        if self.keys_to_keep:
            return self.keys_to_keep
        else:
            return [f[0] for f in self.transformer_funcs if f[0]]

    @staticmethod
    def combine_dataframes(list_of_dataframes):
        combined_dataframes = reduce(
            lambda l, r: pd.merge(l, r, left_index=True, right_index=True, how='outer'),
            list_of_dataframes
        )
        return combined_dataframes
