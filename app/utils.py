from functools import wraps

import numpy as np
import pandas as pd


def dash_kwarg(inputs):
    def accept_func(func):
        @wraps(func)
        def wrapper(*args):
            input_names = [item.component_id for item in inputs]
            kwargs_dict = dict(zip(input_names, args))
            return func(**kwargs_dict)

        return wrapper

    return accept_func


def skewness(dist):
    try:
        result = dist.moment(3) / dist.std() ** 3
    except:
        result = np.nan
    return result


def kurtosis(dist):
    try:
        result = dist.moment(4) / dist.std() ** 4
    except:
        result = np.nan
    return result


def dist_summary(dist, name):
    mean = dist.mean()
    std = dist.std()
    var = dist.var()
    skew = skewness(dist)
    kurt = kurtosis(dist)
    return pd.Series({'name': name,
                      'mean': mean,
                      'std': std,
                      'variance': var,
                      'skewness': skew,
                      'kurtosis': kurt})


def dist_summary_dict(dist, name):
    mean = dist.mean()
    std = dist.std()
    var = dist.vat()
    skew = skewness(dist)
    kurt = kurtosis(dist)
