"""Compute optimal and average improvement for different parameters."""

from math import floor, nan

import numpy as np

from bound_evaluation.array_to_results import two_col_array_to_results
from bound_evaluation.compare_old_new import compute_improvement
from fat_tree.fat_cross_perform import FatCrossPerform
from nc_arrivals.arrival_enum import ArrivalEnum
from nc_arrivals.qt import DM1
from nc_operations.perform_enum import PerformEnum
from nc_service.constant_rate_server import ConstantRate
from optimization.opt_method import OptMethod
from utils.perform_parameter import PerformParameter

########################################################################
# Find Optimal Parameters
########################################################################


def grid_param_simple_exp(delay: int, opt_method: OptMethod, metric: str,
                          lamb1_range, lamb2_range, rate1_range,
                          rate2_range) -> dict:
    """Choose parameters along a grid."""
    total_iterations = len(lamb1_range) * len(lamb2_range) * len(
        rate1_range) * len(rate2_range)

    param_array = np.empty([total_iterations, 4])
    res_array = np.empty([total_iterations, 2])

    i = 0
    for lamb1 in lamb1_range:
        for lamb2 in lamb2_range:
            for rate1 in rate1_range:
                for rate2 in rate2_range:
                    delay_prob = PerformParameter(
                        perform_metric=PerformEnum.DELAY_PROB, value=delay)

                    setting = FatCrossPerform(
                        arr_list=[DM1(lamb=lamb1),
                                  DM1(lamb=lamb2)],
                        ser_list=[
                            ConstantRate(rate=rate1),
                            ConstantRate(rate=rate2)
                        ],
                        perform_param=delay_prob)
                    param_array[i, 0] = lamb1
                    param_array[i, 1] = lamb2
                    param_array[i, 2] = rate1
                    param_array[i, 3] = rate2

                    # bound, new_bound
                    res_array[i, 0], res_array[i, 1] = compute_improvement(
                        setting=setting, opt_method=opt_method, number_l=1)

                    # This might be a very dangerous condition
                    if (res_array[i, 1] >= 1 or res_array[i, 0] == nan
                            or res_array[i, 1] == nan):
                        res_array[i, ] = nan

                    if i % floor(total_iterations / 10) == 0:
                        print("iteration {0} of {1}".format(
                            i, total_iterations))

                    i += 1

    return two_col_array_to_results(
        arrival_enum=ArrivalEnum.DM1,
        metric=metric,
        param_array=param_array,
        res_array=res_array,
        number_servers=2)


if __name__ == '__main__':
    print(
        grid_param_simple_exp(
            delay=4,
            opt_method=OptMethod.GRID_SEARCH,
            metric="relative",
            lamb1_range=[0.1, 0.3, 0.5, 1, 2, 4, 8],
            lamb2_range=[0.1, 0.3, 0.5, 1, 2, 4, 8],
            rate1_range=[0.1, 0.3, 0.5, 1, 2, 4, 8],
            rate2_range=[0.1, 0.3, 0.5, 1, 2, 4, 8]))
