"""Helper functions"""

from itertools import product
from typing import List

import numpy as np
import pandas as pd

from utils.exceptions import ParameterOutOfBounds

EPSILON = 1e-09


def get_q(p: float, indep: bool) -> float:
    """

    :param p: Hoelder p
    :param indep: if true, p=q=1, else q = p / (p - 1)
    :return: q
    """
    if indep:
        return 1.0
    else:
        if p <= 1:
            raise ParameterOutOfBounds("p={0} must be >1".format(p))

        # 1/p + 1/q = 1
        # 1/q = (p - 1) / p

        return p / (p - 1)


def get_p_n(p_list: List[float], indep: bool) -> float:
    """

    :param p_list: first p_1, ..., p_n in generalized Hoelder inequality
    :param indep: if true, all p_i = 1, else 1 / (sum p_i) = 1
    :return: last p_n
    """
    if indep:
        return 1.0
    else:
        for p_i in p_list:
            if p_i <= 1:
                raise ParameterOutOfBounds("p={0} must be >1".format(p_i))

        return 1 / (1 - sum(p_list))


def is_equal(float1: float, float2: float) -> bool:
    """
    :param float1: real 1
    :param float2: real 2
    :return: returns true if distance is less than epsilon
    """
    return abs(float1 - float2) < EPSILON


def expand_grid(list_input: list) -> pd.DataFrame:
    """
    implement R-expand.grid() function
    :param list_input: list of values to be expanded
    :return:           expanded data frame
    """
    return pd.DataFrame([row for row in product(*list_input)])


def centroid_without_one_row(simplex: np.ndarray, index: int) -> np.ndarray:
    # type hint does not work with int and np.ndarray[int]
    # column mean of simplex without a given row
    # (usually the one with the worst y-to_value)
    return np.delete(simplex, index, 0).mean(axis=0)


def average_towards_best_row(simplex: np.ndarray, best_index: int,
                             shrink_factor: float) -> np.ndarray:
    # type hint does not work with int and np.ndarray[int]
    index = 0
    for row in simplex:
        simplex[index] = simplex[best_index] + shrink_factor * (
            row - simplex[best_index])
        index += 1

    return simplex


def get_unit_vector(length: int, index: int) -> List[float]:
    """

    :param length: length of unit vector
    :param index:  index of 1.0 to_value
    :return:       unit vector with 1.0 at index and 0.0 else
    """
    res = [0.0] * length
    res[index] = 1.0

    return res


if __name__ == '__main__':
    SIMPLEX_START_TEST = np.array([[0.1, 2.0], [1.0, 3.0], [2.0, 2.0]])
    print(SIMPLEX_START_TEST)
    print(centroid_without_one_row(simplex=SIMPLEX_START_TEST, index=0))
    print(
        average_towards_best_row(
            SIMPLEX_START_TEST, best_index=0, shrink_factor=0.5))
