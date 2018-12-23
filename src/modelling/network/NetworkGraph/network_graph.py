from modelling.network.flow.path import Path
from modelling.network.link.link import Link
from modelling.network.network import Network
from modelling.network.server.server import Server
from modelling.network.ServerGraph.server_graph import ServerGraph

class NetworkGraph(Network):

    def find_shortest_path(self) -> Path:
        pass

    def __init__(self):
        super().__init__()

    def to_server_graph(self):
        # TODO conversion from network graph to server graph
        return ServerGraph()

    def add_link(self, src: Server, dst: Server) -> Link:
        super().add_link(src, dst)
        return super().add_link(dst, src)
