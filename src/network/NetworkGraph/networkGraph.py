from network.ServerGraph.serverGraph import ServerGraph
from network.flow.path import Path
from network.link.link import Link
from network.network import Network
from network.server.server import Server


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
