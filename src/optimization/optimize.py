"""Optimize theta and all Lyapunov l's"""

from math import exp, inf
from typing import List, Tuple
from warnings import warn

import numpy as np
import pandas as pd
import scipy.optimize

from library.deprecated import deprecated
from library.exceptions import ParameterOutOfBounds
from library.helper_functions import (
    average_towards_best_row, centroid_without_one_row, expand_grid, is_equal)
from library.setting import Setting
from optimization.nelder_mead_parameters import NelderMeadParameters
from optimization.simul_annealing import SimulAnnealing


class Optimize(object):
    """Optimize class"""

    def __init__(self, setting: Setting, print_x=False) -> None:
        self.setting = setting
        self.print_x = print_x

    def eval_except(self, param_list: List[float]) -> float:
        """
        Shortens the exception handling and case distinction in a small method.

        :param param_list: theta parameter and Lyapunov parameters l_i
        :return:           function to_value
        """

        try:
            return self.setting.bound(param_list=param_list)
        except (FloatingPointError, OverflowError, ParameterOutOfBounds):
            return inf

    def grid_search(self, bound_list: List[Tuple[float, float]],
                    delta: float) -> float:
        """
        Search optimal values along a grid in the parameter space.

        :param bound_list: list of tuples of lower and upper bounds
        :param delta:      granularity of the grid search
        :return:           optimized bound
        """

        list_slices = [slice(0)] * len(bound_list)

        for i in range(len(bound_list)):
            list_slices[i] = slice(bound_list[i][0], bound_list[i][1], delta)

        np.seterr("raise")

        # grid_res = scipy.optimize.brute(
        #     func=self.eval_except, ranges=tuple(list_slices),
        #     full_output=True)

        try:
            grid_res = scipy.optimize.brute(
                func=self.eval_except,
                ranges=tuple(list_slices),
                full_output=True)

        except FloatingPointError:
            return inf

        for i in range(len(bound_list)):
            if is_equal(grid_res[0][i], bound_list[i][0]) or is_equal(
                    grid_res[0][i], bound_list[i][1]):
                warn("optimal x is on the boundary: {0}".format(
                    str(grid_res[0][i])))

        if self.print_x:
            print("grid search optimal x: {0}".format(grid_res[0].tolist()))

        return grid_res[1]

    def pattern_search(self,
                       start_list: List[float],
                       delta: float = 3.0,
                       delta_min: float = 0.01) -> float:
        """
        Optimization in Hooke and Jeeves.

        :param start_list: list of starting values
        :param delta:      initial granularity
        :param delta_min:  final granularity
        :return:           optimized bound
        """

        optimum_current = self.eval_except(param_list=start_list)

        optimum_new = optimum_current

        param_list = start_list[:]
        param_new = param_list[:]

        while delta > delta_min:
            for index, value in enumerate(param_list):
                param_new[index] = value + delta
                candidate_plus = self.eval_except(param_list=param_new)

                param_new[index] = value - delta
                candidate_minus = self.eval_except(param_list=param_new)

                if candidate_plus < optimum_new:
                    param_new[index] = value + delta
                    optimum_new = candidate_plus
                elif candidate_minus < optimum_new:
                    param_new[index] = value - delta
                    optimum_new = candidate_minus

            if optimum_new < optimum_current:
                # i.e., exploration step was successful
                param_old = param_list[:]
                param_list = param_new[:]
                optimum_current = optimum_new
                for index, value in enumerate(param_new):
                    param_new[index] = 2 * param_list[index] - param_old[index]

                # try a pattern step
                candidate_new = self.eval_except(param_list=param_new)

                if candidate_new < optimum_current:
                    param_list = param_new[:]
                    optimum_current = optimum_new
            else:
                param_new = param_list[:]
                delta *= 0.5

        if self.print_x:
            print("pattern search optimal x: {0}".format(param_list))

        return optimum_new

    def nelder_mead(self, simplex: np.ndarray, sd_min: float = 10
                    **(-2)) -> float:
        """
        Nelder-Mead optimization from the sciPy package.

        :param simplex:     initial parameter simplex
        :param sd_min:      abort criterion (detect when the changes
                            become very small)
        :return:            optimized bound
        """
        np.seterr("raise")
        try:
            nm_res = scipy.optimize.minimize(
                self.eval_except,
                x0=np.zeros(shape=(1, simplex.shape[1])),
                method='Nelder-Mead',
                options={
                    'initial_simplex': simplex,
                    'fatol': sd_min
                })

        except FloatingPointError:
            return inf

        if self.print_x:
            print("Nelder Mead optimal x: {0}".format(nm_res.x))

        return nm_res.fun

    def basin_hopping(self, start_list: List[float]) -> float:
        """
        Basin Hopping optimization from the sciPy package.

        :param start_list:  initial guess
        :return:            optimized bound
        """
        try:
            bh_res = scipy.optimize.basinhopping(
                func=self.eval_except, x0=start_list)

        except FloatingPointError:
            return inf

        if self.print_x:
            print("Basin Hopping optimal x: {0}".format(bh_res.x))

        return bh_res.fun

    def simulated_annealing(self, start_list: List[float],
                            simul_annealing: SimulAnnealing) -> float:
        """

        :param start_list:       initial parameter set
        :param simul_annealing:  object that contains all the simulated
                                 annealing-parameters and helper methods
        :return:                 optimized bound
        """

        param_list = start_list[:]
        optimum_current = self.eval_except(param_list=param_list)

        param_best = param_list[:]
        optimum_best = optimum_current

        temperature = simul_annealing.temp_start
        rep_max = simul_annealing.rep_max
        search_radius = simul_annealing.search_radius

        objective_change = True

        while objective_change:
            objective_change = False
            random_numbers = np.random.uniform(size=rep_max)

            for iteration in range(rep_max):
                param_new = simul_annealing.search_feasible_neighbor(
                    objective=self.eval_except,
                    input_list=param_list,
                    search_radius=search_radius)
                optimum_new = self.eval_except(param_list=param_new)

                if optimum_new < optimum_current:
                    optimum_current = optimum_new
                    param_list = param_new[:]
                    objective_change = True
                    if optimum_new < optimum_best:
                        param_best = param_new[:]
                        optimum_best = optimum_new
                else:
                    if exp((optimum_current - optimum_new) /
                           temperature) > random_numbers[iteration]:
                        # even if we compute inf - inf, Python does not
                        # lead to an error
                        param_list = param_new[:]
                        optimum_current = optimum_new
                        # Due to the fact that objective_new > objective, we
                        # have exp(-c/temperature), which is decreasing
                        # in the temperature
                        objective_change = True

            temperature *= simul_annealing.cooling_factor

        if self.print_x:
            print("simulated annealing optimal x: {0}".format(param_best))

        return optimum_best

    def differential_evolution(self, bound_list: List[tuple]) -> float:
        """
        Differential Evolution optimization from the sciPy package.

        :param bound_list: list of tuples of lower and upper bounds
        :return:           optimized bound
        """
        np.seterr("raise")

        try:
            de_res = scipy.optimize.differential_evolution(
                func=self.eval_except, bounds=bound_list)

        except FloatingPointError:
            return inf

        if self.print_x:
            print("Differential Evolution optimal x: {0}".format(de_res.x))

        return de_res.fun

    def bfgs(self, start_list: list) -> float:
        x0 = np.array(start_list)

        np.seterr("raise")

        try:
            bfgs_res = scipy.optimize.minimize(
                fun=self.eval_except, x0=x0, method="BFGS")

        except FloatingPointError:
            return inf

        if self.print_x:
            print("BFGS optimal x: {0}".format(bfgs_res.x))

        return bfgs_res.fun

    @deprecated
    def grid_search_old(self, bound_list: List[Tuple[float, float]],
                        delta: float) -> float:
        """
        Search optimal values along a grid in the parameter space.

        :param bound_list: list of tuples of lower and upper bounds
        :param delta:      granularity of the grid search
        :return:           optimized bound
        """
        # first = lower bound
        # second = upper bound

        param_list = [[]] * len(bound_list)

        for index, value in enumerate(bound_list):
            param_list[index] = np.arange(
                start=value[0], stop=value[1] + 10**(-10),
                step=delta).tolist()

        # each entry in the dictionary consists of lower and upper bounds

        param_grid_df: pd.DataFrame = expand_grid(list_input=param_list)

        number_values = param_grid_df.shape[0]

        y_opt = inf
        opt_row = 0

        for row in range(number_values):
            candidate_opt = self.eval_except(
                param_list=param_grid_df.values.tolist()[row])
            if candidate_opt < y_opt:
                y_opt = candidate_opt
                opt_row = row

        for i in range(len(bound_list)):
            if is_equal(param_grid_df.iloc[opt_row][i],
                        bound_list[i][0]) or is_equal(
                            param_grid_df.iloc[opt_row][i], bound_list[i][1]):
                warn("GS old optimal x is on the boundary: {0}".format(
                    str(param_grid_df.iloc[opt_row][i])))

        if self.print_x:
            print("GS old optimal x: {0}".format(
                param_grid_df.iloc[opt_row].tolist()))

        return y_opt

    @deprecated
    def nelder_mead_old(self,
                        simplex: np.ndarray,
                        nelder_mead_param: NelderMeadParameters,
                        sd_min: float = 10**(-2)):
        """
        Nelder-Mead Optimization.

        :param simplex:            initial parameter simplex
        :param nelder_mead_param:  object that contains all the
                                   Nelder-Mead-parameters
        :param sd_min:             abort criterion (detect when the changes
                                   become very small)
        :return:                   optimized bound
        """
        number_rows = simplex.shape[0]
        number_columns = simplex.shape[1]
        # number of rows is the number of points = number of columns + 1
        # number of columns is the number of parameters
        if number_rows is not number_columns + 1:
            raise ValueError(
                "array argument is not a simplex, rows: {0}, columns: {1}".
                format(number_rows, number_columns))

        reflection_alpha = nelder_mead_param.reflection_alpha
        expansion_gamma = nelder_mead_param.expansion_gamma
        contraction_beta = nelder_mead_param.contraction_beta
        shrink_gamma = nelder_mead_param.shrink_gamma

        # print("simplex_start", simplex)
        # print("centroid", centroid_without_one_row(simplex=simplex, index=0))

        y_value = np.empty(number_rows)

        index = 0
        # print(simplex_start)
        for row in simplex:
            # print("row = ", row)
            y_value[index] = self.eval_except(param_list=row)
            index += 1

        # print("y_value: ", y_value)
        best_index: int = np.nanargmin(y_value)
        # print("best index: ", best_index)

        while np.std(y_value, ddof=1) > sd_min:
            # print("simplex = ", simplex)
            # print("y_value = ", y_value)
            # print("standard_deviation of y = ", np.std(y_value, ddof=1))

            worst_index: int = np.argmax(y_value)
            best_index: int = np.argmin(y_value)

            # compute centroid without worst row
            centroid = centroid_without_one_row(
                simplex=simplex, index=worst_index)
            # print("centroid: ", centroid)

            # print("worst_point: ", simplex_start[worst_index])

            p_reflection = (
                1 + reflection_alpha
            ) * centroid - reflection_alpha * simplex[worst_index]

            # print("p_reflection", p_reflection)
            y_p_reflection = self.eval_except(param_list=p_reflection)
            # print("y_p_reflection", y_p_reflection)

            second_worst_index = np.argsort(y_value)[-2]
            # print("second_worst_index", second_worst_index)

            if y_p_reflection < y_value[best_index]:
                p_expansion = expansion_gamma * p_reflection + (
                    1 - expansion_gamma) * centroid
                y_p_expansion = self.eval_except(param_list=p_expansion)

                if y_p_expansion < y_value[best_index]:
                    simplex[worst_index] = p_expansion
                    y_value[worst_index] = y_p_expansion
                else:
                    simplex[worst_index] = p_reflection
                    y_value[worst_index] = y_p_reflection

            elif y_p_reflection > y_value[second_worst_index]:
                if y_p_reflection < y_value[worst_index]:
                    simplex[worst_index] = p_reflection
                    y_value[worst_index] = y_p_reflection

                p_contraction = contraction_beta * simplex[worst_index] + (
                    1 - contraction_beta) * centroid
                y_p_contraction = self.eval_except(param_list=p_contraction)

                if y_p_contraction < y_value[worst_index]:
                    simplex[worst_index] = p_contraction
                    y_value[worst_index] = y_p_contraction

                else:
                    simplex = average_towards_best_row(
                        simplex=simplex,
                        best_index=best_index,
                        shrink_factor=shrink_gamma)
                    index = 0
                    for row in simplex:
                        y_value[index] = self.eval_except(param_list=row)
                        index += 1

            else:
                simplex[worst_index] = p_reflection
                y_value[worst_index] = y_p_reflection

        if self.print_x:
            print("NM old optimal x: {0}".format(simplex[best_index]))

        return y_value[best_index]
