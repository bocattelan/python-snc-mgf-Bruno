import unittest

from modelling.network.NetworkGraph.network_graph import NetworkGraph
from nc_arrivals.markov_modulated import MMOOFluid
from nc_service.constant_rate_server import ConstantRate


class networkGraphCreation(unittest.TestCase):
    service = ConstantRate(10)
    arrival = MMOOFluid(mu=0.5, lamb=0.5, burst=1.5)

    def test_one_node(self):
        network_graph = NetworkGraph()
        s0 = network_graph.add_server("s0", self.service)
        f0 = network_graph.add_flow("f0", self.arrival, [s0])

        self.assertEqual(network_graph.get_servers(), {s0})
        print(network_graph.get_flows())
        self.assertEqual(network_graph.get_flows(), {f0})
