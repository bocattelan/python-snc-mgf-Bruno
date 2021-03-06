"""SFA for canonical tree"""

from typing import List

from nc_arrivals.arrival_distribution import ArrivalDistribution
from nc_operations.evaluate_single_hop import evaluate_single_hop
from nc_operations.operations import Convolve, Leftover
from nc_service.constant_rate_server import ConstantRate
from nc_service.service import Service
from utils.perform_parameter import PerformParameter
from utils.setting import Setting


class TandemSFA(Setting):
    """Canonical tandem with SFA analysis"""

    def __init__(self, arr_list: List[ArrivalDistribution],
                 ser_list: List[ConstantRate],
                 perform_param: PerformParameter) -> None:
        # The first element in the arrival list in dedicated to the foi
        if len(arr_list) != (len(ser_list) + 1):
            raise ValueError(
                ("number of arrivals {0} and servers {1} + 1 have to match"
                 ).format(len(arr_list), len(ser_list)))

        self.arr_list = arr_list
        self.ser_list = ser_list
        self.perform_param = perform_param
        self.number_servers = len(ser_list)

    def bound(self, param_list: List[float]) -> float:
        theta = param_list[0]

        leftover_service_list: List[Service] = [
            Leftover(arr=self.arr_list[i + 1], ser=self.ser_list[i])
            for i in range(self.number_servers)
        ]

        s_net: Service = leftover_service_list[0]
        for i in range(1, self.number_servers):
            s_net = Convolve(s_net, leftover_service_list[i])

        return evaluate_single_hop(
            foi=self.arr_list[0],
            s_net=s_net,
            theta=theta,
            perform_param=self.perform_param)
