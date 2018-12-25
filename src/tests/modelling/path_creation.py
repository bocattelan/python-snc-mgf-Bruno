import unittest

from modelling.network.NetworkGraph.network_graph import NetworkGraph
from nc_arrivals.markov_modulated import MMOOFluid
from nc_service.constant_rate_server import ConstantRate


class pathCreation(unittest.TestCase):
    service = ConstantRate(10)
    arrival = MMOOFluid(mu=0.5, lamb=0.5, burst=1.5)

    def test_binary_tree(self):
        network_graph = NetworkGraph()
        s0 = network_graph.add_server("s0")
        s1 = network_graph.add_server("s1")
        s2 = network_graph.add_server("s2")
        s3 = network_graph.add_server("s3")
        s4 = network_graph.add_server("s4")
        s5 = network_graph.add_server("s5")
        s6 = network_graph.add_server("s6")
        s7 = network_graph.add_server("s7")
        s8 = network_graph.add_server("s8")

        network_graph.add_link(s0, s1, self.service)
        network_graph.add_link(s0, s2, self.service)

        network_graph.add_link(s1, s3, self.service)
        network_graph.add_link(s1, s4, self.service)

        network_graph.add_link(s3, s5, self.service)
        network_graph.add_link(s3, s6, self.service)

        network_graph.add_link(s4, s7, self.service)
        network_graph.add_link(s4, s8, self.service)

        self.assertEqual([s0, s1, s3, s5], network_graph.find_shortest_path(s0, s5))
        self.assertEqual({s0, s1, s2, s3, s4, s5, s6, s7, s8}, network_graph.servers)
