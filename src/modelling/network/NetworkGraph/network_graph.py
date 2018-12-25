from collections import deque
from typing import List

from modelling.network.flow.path import Path
from modelling.network.link.link import Link
from modelling.network.network import Network
from modelling.network.server.server import Server
from modelling.network.ServerGraph.server_graph import ServerGraph
from nc_service.service import Service
from utils.values import Values


class NetworkGraph(Network):

    # code from: http://www.rosettacode.org/wiki/Dijkstra%27s_algorithm#Python
    def find_shortest_path(self, src: Server, dst: Server) -> List[Server]:
        dist = {vertex: Values.POSITIVE_INFINITY for vertex in self.servers}
        previous = {vertex: None for vertex in self.servers}
        dist[src] = 0
        q = self.servers.copy()
        neighbours = {vertex: set() for vertex in self.servers}
        for link in self.links:
            neighbours[link.src].add((link.dst, 1))
        # pp(neighbours)

        while q:
            u = min(q, key=lambda vertex: dist[vertex])
            q.remove(u)
            if dist[u] == Values.POSITIVE_INFINITY or u == dst:
                break
            for v, cost in neighbours[u]:
                alt = dist[u] + cost
                if alt < dist[v]:  # Relax (u,v,a)
                    dist[v] = alt
                    previous[v] = u
        # pp(previous)
        s, u = deque(), dst
        while previous[u]:
            s.appendleft(u)
            u = previous[u]
        s.appendleft(u)
        return list(s)

    def __init__(self):
        super().__init__()

    def to_server_graph(self):
        # TODO conversion from network graph to server graph
        return ServerGraph()

    def add_link(self, src: Server, dst: Server, service: Service) -> Link:
        super().add_link(src, dst, service)
        return super().add_link(dst, src, service)
