from functools import reduce
import pandas as pd


class Pipeline:

    def __init__(self, transformer_funcs):
        self.transformer_funcs = transformer_funcs

    def transform(self, data):
        for name, func, kwargs in self.transformer_funcs:
            if name:
                print(f'Creating feature {name}')
                data[name] = func(data, **kwargs)
            else:
                print(f'Applying modifier {func.__name__}')
                data = func(data, **kwargs)

        feature_names = [f[0] for f in self.transformer_funcs if f[0]]
        data = self.combine_dataframes([data[k] for k in feature_names])
        return data

    @staticmethod
    def combine_dataframes(list_of_dataframes):
        combined_dataframes = reduce(
            lambda l, r: pd.merge(l, r, left_index=True, right_index=True, how='outer'),
            list_of_dataframes
        )
        return combined_dataframes
