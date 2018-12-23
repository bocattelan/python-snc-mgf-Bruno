from modelling.network.flow.path import Path
from modelling.network.link.link import Link
from modelling.network.network import Network
from modelling.network.server.server import Server


class ServerGraph(Network):

    def __init__(self):
        super().__init__()

    def find_shortest_path(self) -> Path:
        pass

    def add_link(self, src: Server, dst: Server) -> Link:
        return super().add_link(src, dst)
