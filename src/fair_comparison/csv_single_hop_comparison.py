"""Compare Delay for different bounds for regulated Arrivals"""

import csv
from typing import List

import pandas as pd

from nc_arrivals.regulated_arrivals import (LeakyBucketMassOne,
                                            LeakyBucketMassTwo,
                                            LeakyBucketMassTwoExact,
                                            TokenBucketConstant)
from nc_operations.dnc_performance_bounds import fifo_delay
from nc_operations.perform_enum import PerformEnum
from nc_service.constant_rate_server import ConstantRate
from optimization.opt_method import OptMethod
from optimization.optimize import Optimize
from single_server.single_server_perform import SingleServerPerform
from utils.perform_param_list import PerformParamList
from utils.perform_parameter import PerformParameter


def single_hop_comparison(
        aggregation: int, sigma_single: float, rho_single: float,
        service_rate: float, perform_param: PerformParameter,
        opt_method: OptMethod) -> (float, float, float, float, float):

    print_x = False
    constant_rate_server = ConstantRate(service_rate)

    tb_const = TokenBucketConstant(
        sigma_single=sigma_single, rho_single=rho_single, n=aggregation)

    dnc_fifo_single: float = fifo_delay(
        token_bucket_constant=tb_const, constant_rate=constant_rate_server)

    const_single = SingleServerPerform(
        arr=tb_const,
        const_rate=constant_rate_server,
        perform_param=perform_param)

    leaky_mass_1 = SingleServerPerform(
        arr=LeakyBucketMassOne(
            sigma_single=sigma_single, rho_single=rho_single, n=aggregation),
        const_rate=constant_rate_server,
        perform_param=perform_param)

    leaky_mass_2 = SingleServerPerform(
        arr=LeakyBucketMassTwo(
            sigma_single=sigma_single, rho_single=rho_single, n=aggregation),
        const_rate=constant_rate_server,
        perform_param=perform_param)

    exact_mass_2 = SingleServerPerform(
        arr=LeakyBucketMassTwoExact(
            sigma_single=sigma_single, rho_single=rho_single, n=aggregation),
        const_rate=constant_rate_server,
        perform_param=perform_param)

    bound_list = [(0.05, 15.0)]
    delta = 0.05

    if opt_method == OptMethod.GRID_SEARCH:
        const_opt = Optimize(
            setting=const_single, print_x=print_x).grid_search(
                bound_list=bound_list, delta=delta)

        leaky_mass_1_opt = Optimize(
            setting=leaky_mass_1, print_x=print_x).grid_search(
                bound_list=bound_list, delta=delta)

        leaky_mass_2_opt = Optimize(
            setting=leaky_mass_2, print_x=print_x).grid_search(
                bound_list=bound_list, delta=delta)

        exact_mass_2_opt = Optimize(
            setting=exact_mass_2, print_x=print_x).grid_search(
                bound_list=bound_list, delta=delta)

    else:
        raise NameError("Optimization parameter {0} is infeasible".format(
            opt_method.name))

    return (dnc_fifo_single, const_opt, leaky_mass_1_opt, leaky_mass_2_opt,
            exact_mass_2_opt)


def compare_aggregation(aggregations: List[int], sigma_single: float,
                        rho_single: float, service_rate: float,
                        perform_param: PerformParameter,
                        opt_method: OptMethod) -> pd.DataFrame:
    dnc_fifo_single = [0.0] * len(aggregations)
    const_opt = [0.0] * len(aggregations)
    leaky_mass_1 = [0.0] * len(aggregations)
    leaky_mass_2_opt = [0.0] * len(aggregations)
    exact_mass_2_opt = [0.0] * len(aggregations)

    for i, agg in enumerate(aggregations):
        dnc_fifo_single[i], const_opt[i], leaky_mass_1[i], leaky_mass_2_opt[
            i], exact_mass_2_opt[i] = single_hop_comparison(
                aggregation=agg,
                sigma_single=sigma_single,
                rho_single=rho_single,
                service_rate=service_rate * agg,
                perform_param=perform_param,
                opt_method=opt_method)

    results_df = pd.DataFrame(
        {
            "DNCBound": dnc_fifo_single,
            "constBound": const_opt,
            "leakyMassOne": leaky_mass_1,
            "leakyMassTwo": leaky_mass_2_opt,
            "exactMassTwo": exact_mass_2_opt
        },
        index=aggregations)

    filename = (
        "regulated_single_{0}_sigma_{1}_rho_{2}_utilization_{3}_{4}").format(
            perform_param.to_name_value(), str(sigma_single), str(rho_single),
            str("%.2f" % (rho_single / service_rate)), opt_method.name)

    results_df.to_csv(
        filename + '.csv', index=True, quoting=csv.QUOTE_NONNUMERIC)

    return results_df


def compare_probability(aggregation: int, sigma_single: float,
                        rho_single: float, service_rate: float,
                        perform_list: PerformParamList,
                        opt_method: OptMethod) -> pd.DataFrame:
    dnc_fifo_single = [0.0] * len(perform_list.values_list)
    const_opt = [0.0] * len(perform_list.values_list)
    leaky_mass_1 = [0.0] * len(perform_list.values_list)
    leaky_mass_2_opt = [0.0] * len(perform_list.values_list)
    exact_mass_2_opt = [0.0] * len(perform_list.values_list)

    for _i in range(len(perform_list.values_list)):
        dnc_fifo_single[_i], const_opt[_i], leaky_mass_1[_i], leaky_mass_2_opt[
            _i], exact_mass_2_opt[_i] = single_hop_comparison(
                aggregation=aggregation,
                sigma_single=sigma_single,
                rho_single=rho_single,
                service_rate=service_rate * aggregation,
                perform_param=perform_list.get_parameter_at_i(_i),
                opt_method=opt_method)

    results_df = pd.DataFrame(
        {
            "DNCBound": dnc_fifo_single,
            "constBound": const_opt,
            "leakyMassOne": leaky_mass_1,
            "leakyMassTwo": leaky_mass_2_opt,
            "exactMassTwo": exact_mass_2_opt
        },
        index=perform_list.values_list)

    filename = (
        "regulated_single_{0}_n_{1}_sigma_{2}_rho_{3}_utilization_{4}_{5}"
    ).format(perform_list.to_name(), aggregation, str(sigma_single),
             str(rho_single), str("%.2f" % (rho_single / service_rate)),
             opt_method.name)

    results_df.to_csv(
        filename + '.csv', index=True, quoting=csv.QUOTE_NONNUMERIC)

    return results_df


def compare_sigma(aggregation: int, sigmas: List[float], rho_single: float,
                  service_rate: float, perform_param: PerformParameter,
                  opt_method: OptMethod) -> pd.DataFrame:
    dnc_fifo_single = [0.0] * len(sigmas)
    const_opt = [0.0] * len(sigmas)
    leaky_mass_1 = [0.0] * len(sigmas)
    leaky_mass_2_opt = [0.0] * len(sigmas)
    exact_mass_2_opt = [0.0] * len(sigmas)

    for i, sigma in enumerate(sigmas):
        dnc_fifo_single[i], const_opt[i], leaky_mass_1[i], leaky_mass_2_opt[
            i], exact_mass_2_opt[i] = single_hop_comparison(
                aggregation=aggregation,
                sigma_single=sigma,
                rho_single=rho_single,
                service_rate=service_rate * aggregation,
                perform_param=perform_param,
                opt_method=opt_method)

    results_df = pd.DataFrame(
        {
            "DNCBound": dnc_fifo_single,
            "constBound": const_opt,
            "leakyMassOne": leaky_mass_1,
            "leakyMassTwo": leaky_mass_2_opt,
            "exactMassTwo": exact_mass_2_opt
        },
        index=sigmas)

    filename = "regulated_single_{0}_n_{1}_rho_{2}_utilization_{3}_{4}".format(
        perform_param.to_name_value(), str(aggregation), str(rho_single),
        str("%.2f" % (rho_single / service_rate)), opt_method.name)

    results_df.to_csv(
        filename + '.csv', index=True, quoting=csv.QUOTE_NONNUMERIC)

    return results_df


if __name__ == '__main__':
    DELAY6 = PerformParameter(perform_metric=PerformEnum.DELAY, value=10**(-6))

    NUMBER_AGGREGATIONS = [2, 5, 10, 15, 20, 25, 30, 35, 40, 50]

    RHO_SINGLE = 0.1
    SERVICE_RATE = 0.12
    SIGMA_VALUES_1 = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 15.0, 18.0, 20.0]

    for SIGMA_1 in SIGMA_VALUES_1:
        print(
            compare_aggregation(
                aggregations=NUMBER_AGGREGATIONS,
                sigma_single=SIGMA_1,
                rho_single=RHO_SINGLE,
                service_rate=SERVICE_RATE,
                perform_param=DELAY6,
                opt_method=OptMethod.GRID_SEARCH))

    PERFORM_LIST = PerformParamList(
        perform_metric=PerformEnum.DELAY,
        values_list=[
            10**(-3), 10**(-6), 10**(-9), 10**(-12), 10**(-15), 10**(-18), 10
            **(-21), 10**(-24), 10**(-27), 10**(-30)
        ])

    SIGMA_VALUES_2 = [3.0, 5.0, 10.0, 15.0, 18.0, 20.0, 50.0, 100.0]

    for SIGMA_2 in SIGMA_VALUES_2:
        print(
            compare_probability(
                aggregation=20,
                sigma_single=SIGMA_2,
                rho_single=RHO_SINGLE,
                service_rate=SERVICE_RATE,
                perform_list=PERFORM_LIST,
                opt_method=OptMethod.GRID_SEARCH))

    SIGMA_VALUES_3 = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 15.0, 18.0, 20.0]

    print(
        compare_sigma(
            aggregation=100,
            sigmas=SIGMA_VALUES_3,
            rho_single=RHO_SINGLE,
            service_rate=SERVICE_RATE,
            perform_param=DELAY6,
            opt_method=OptMethod.GRID_SEARCH))
