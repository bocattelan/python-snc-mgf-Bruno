"""Compare standard bound with Lyapunov bound."""

from math import nan
from timeit import default_timer as timer
from typing import List

from nc_arrivals.arrival_distribution import ArrivalDistribution
from nc_operations.perform_enum import PerformEnum
from optimization.initial_simplex import InitialSimplex
from optimization.opt_method import OptMethod
from optimization.optimize import Optimize
from optimization.optimize_new import OptimizeNew
from optimization.sim_anneal_param import SimAnnealParams
from utils.setting_new import SettingNew


def compute_improvement(setting: SettingNew,
                        opt_method: OptMethod,
                        number_l=1,
                        print_x=False,
                        show_warn=False) -> tuple:
    """Compare standard_bound with the new Lyapunov bound."""

    if opt_method == OptMethod.GRID_SEARCH:
        theta_bounds = [(0.1, 4.0)]

        standard_bound = Optimize(
            setting=setting, print_x=print_x, show_warn=show_warn).grid_search(
                bound_list=theta_bounds, delta=0.1)

        bound_array = theta_bounds[:]
        for _i in range(1, number_l + 1):
            bound_array.append((0.9, 4.0))

        new_bound = OptimizeNew(
            setting_new=setting, print_x=print_x,
            show_warn=show_warn).grid_search(
                bound_list=bound_array, delta=0.1)

    elif opt_method == OptMethod.PATTERN_SEARCH:
        theta_start = 0.5

        start_list = [theta_start]

        standard_bound = Optimize(
            setting=setting, print_x=print_x,
            show_warn=show_warn).pattern_search(
                start_list=start_list, delta=3.0, delta_min=0.01)

        start_list_new = [theta_start] + [1.0] * number_l

        new_bound = OptimizeNew(
            setting_new=setting, print_x=print_x,
            show_warn=show_warn).pattern_search(
                start_list=start_list_new, delta=3.0, delta_min=0.01)

        # This part is there to overcome opt_method issues
        if new_bound > standard_bound:
            new_bound = standard_bound

    elif opt_method == OptMethod.NELDER_MEAD:
        theta_start = 0.5

        start_list = [theta_start]
        start_simplex = InitialSimplex(parameters_to_optimize=1).gao_han(
            start_list=start_list)

        standard_bound = Optimize(
            setting=setting, print_x=print_x, show_warn=show_warn).nelder_mead(
                simplex=start_simplex, sd_min=10**(-2))

        start_list_new = [theta_start] + [1.0] * number_l
        start_simplex_new = InitialSimplex(
            parameters_to_optimize=number_l + 1).gao_han(
                start_list=start_list_new)

        new_bound = OptimizeNew(
            setting_new=setting, print_x=print_x,
            show_warn=show_warn).nelder_mead(
                simplex=start_simplex_new, sd_min=10**(-2))

        # This part is there to overcome opt_method issues
        if new_bound > standard_bound:
            new_bound = standard_bound

    elif opt_method == OptMethod.BASIN_HOPPING:
        theta_start = 0.5

        start_list = [theta_start]

        standard_bound = Optimize(
            setting=setting, print_x=print_x,
            show_warn=show_warn).basin_hopping(start_list=start_list)

        start_list_new = [theta_start] + [1.0] * number_l

        new_bound = OptimizeNew(
            setting_new=setting, print_x=print_x,
            show_warn=show_warn).basin_hopping(start_list=start_list_new)

        # This part is there to overcome opt_method issues
        if new_bound > standard_bound:
            new_bound = standard_bound

    elif opt_method == OptMethod.SIMULATED_ANNEALING:
        simul_anneal_param = SimAnnealParams()
        theta_start = 0.5

        start_list = [theta_start]

        standard_bound = Optimize(
            setting=setting, print_x=print_x,
            show_warn=show_warn).sim_annealing(
                start_list=start_list, sim_anneal_params=simul_anneal_param)

        start_list_new = [theta_start] + [1.0] * number_l

        new_bound = OptimizeNew(
            setting_new=setting, print_x=print_x,
            show_warn=show_warn).sim_annealing(
                start_list=start_list_new,
                sim_anneal_params=simul_anneal_param)

        # This part is there to overcome opt_method issues
        if new_bound > standard_bound:
            new_bound = standard_bound

    elif opt_method == OptMethod.DIFFERENTIAL_EVOLUTION:
        theta_bounds = [(0.1, 8.0)]

        standard_bound = Optimize(
            setting=setting,
            print_x=print_x).diff_evolution(bound_list=theta_bounds)

        bound_array = theta_bounds[:]
        for _i in range(1, number_l + 1):
            bound_array.append((0.9, 8.0))

        new_bound = OptimizeNew(
            setting_new=setting,
            print_x=print_x).diff_evolution(bound_list=bound_array)

    else:
        raise NameError(
            f"Optimization parameter {opt_method.name} is infeasible")

    # This part is there to overcome opt_method issues
    if new_bound > standard_bound:
        new_bound = standard_bound

    if standard_bound == 0 or new_bound == 0:
        standard_bound = nan
        new_bound = nan

    return standard_bound, new_bound


def compute_overhead(setting: SettingNew, opt_method: OptMethod,
                     number_l=1) -> tuple:
    """Compare computation times."""

    if opt_method == OptMethod.GRID_SEARCH:
        bound_array = [(0.1, 4.0)]

        start = timer()
        Optimize(setting=setting).grid_search(
            bound_list=bound_array, delta=0.1)
        stop = timer()
        time_standard = stop - start

        for _ in range(1, number_l + 1):
            bound_array.append((0.9, 4.0))

        start = timer()
        OptimizeNew(setting_new=setting).grid_search(
            bound_list=bound_array, delta=0.1)
        stop = timer()
        time_lyapunov = stop - start

    elif opt_method == OptMethod.PATTERN_SEARCH:
        start_list = [0.5]

        start = timer()
        Optimize(setting=setting).pattern_search(
            start_list=start_list, delta=3.0, delta_min=0.01)
        stop = timer()
        time_standard = stop - start

        start_list = [0.5] + [1.0] * number_l

        start = timer()
        OptimizeNew(setting_new=setting).pattern_search(
            start_list=start_list, delta=3.0, delta_min=0.01)
        stop = timer()
        time_lyapunov = stop - start

    elif opt_method == OptMethod.NELDER_MEAD:
        start_simplex = InitialSimplex(parameters_to_optimize=1).uniform_dist(
            max_theta=1.0)

        start = timer()
        Optimize(setting=setting).nelder_mead(
            simplex=start_simplex, sd_min=10**(-2))
        stop = timer()
        time_standard = stop - start

        start_simplex_new = InitialSimplex(
            parameters_to_optimize=number_l + 1).uniform_dist(
                max_theta=1.0, max_l=2.0)

        start = timer()
        OptimizeNew(setting_new=setting).nelder_mead(
            simplex=start_simplex_new, sd_min=10**(-2))
        stop = timer()
        time_lyapunov = stop - start

    else:
        raise NameError(
            f"Optimization parameter {opt_method.name} is infeasible")

    return time_standard, time_lyapunov


if __name__ == '__main__':
    from fat_tree.fat_cross_perform import FatCrossPerform
    from utils.perform_parameter import PerformParameter
    from nc_service.constant_rate_server import ConstantRate
    from nc_arrivals.qt import DM1
    from single_server.single_server_perform import SingleServerPerform

    OUTPUT_TIME = PerformParameter(perform_metric=PerformEnum.OUTPUT, value=4)

    EXP_ARRIVAL = DM1(lamb=4.4)
    CONST_RATE = ConstantRate(rate=0.24)

    SETTING1 = SingleServerPerform(
        arr=EXP_ARRIVAL, const_rate=CONST_RATE, perform_param=OUTPUT_TIME)

    # print(
    #     compute_improvement(
    #         setting=SETTING1, opt_method=OptMethod.GRID_SEARCH,
    #         print_x=True))

    DELAY_PROB = PerformParameter(
        perform_metric=PerformEnum.DELAY_PROB, value=4)

    EXP_ARRIVAL1 = DM1(lamb=11.0)
    EXP_ARRIVAL2 = DM1(lamb=9.0)

    CONST_RATE1 = ConstantRate(rate=5.0)
    CONST_RATE2 = ConstantRate(rate=4.0)

    ARR_LIST: List[ArrivalDistribution] = [EXP_ARRIVAL1, EXP_ARRIVAL2]
    SER_LIST: List[ConstantRate] = [CONST_RATE1, CONST_RATE2]

    SETTING2 = FatCrossPerform(
        arr_list=ARR_LIST, ser_list=SER_LIST, perform_param=DELAY_PROB)

    print(
        compute_improvement(
            setting=SETTING2, opt_method=OptMethod.GRID_SEARCH, print_x=True))

    print(
        compute_improvement(
            setting=SETTING2,
            opt_method=OptMethod.PATTERN_SEARCH,
            print_x=True))

    print(
        compute_overhead(
            setting=SETTING2, opt_method=OptMethod.GRID_SEARCH, number_l=1))
