"""MMOO Comparison"""

from nc_arrivals.markov_modulated import MMOODisc, MMOOFluid
from nc_operations.perform_enum import PerformEnum
from nc_service.constant_rate_server import ConstantRate
from optimization.optimize import Optimize
from single_server.single_server_perform import SingleServerPerform
from utils.perform_parameter import PerformParameter

if __name__ == '__main__':
    DELAY_PROB8 = PerformParameter(
        perform_metric=PerformEnum.DELAY_PROB, value=8)

    SINGLE_SERVER = SingleServerPerform(
        arr=MMOOFluid(mu=0.5, lamb=0.5, burst=2.0),
        const_rate=ConstantRate(rate=1.5),
        perform_param=DELAY_PROB8)

    print(
        Optimize(SINGLE_SERVER, print_x=True, show_warn=True).grid_search_old(
            bound_list=[(0.1, 5.0)], delta=0.01))

    print(
        Optimize(SINGLE_SERVER, print_x=True, show_warn=True).grid_search(
            bound_list=[(0.1, 5.0)], delta=0.01))

    SINGLE_SERVER2 = SingleServerPerform(
        arr=MMOODisc(stay_on=0.5, stay_off=0.5, burst=2.0),
        const_rate=ConstantRate(rate=1.5),
        perform_param=DELAY_PROB8)

    print(
        Optimize(SINGLE_SERVER2, print_x=True, show_warn=True).grid_search_old(
            bound_list=[(0.1, 5.0)], delta=0.01))

    print(
        Optimize(SINGLE_SERVER2, print_x=True, show_warn=True).grid_search(
            bound_list=[(0.1, 5.0)], delta=0.01))
