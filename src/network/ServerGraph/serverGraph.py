from network.flow.path import Path
from network.link.link import Link
from network.network import Network
from network.server.server import Server


class ServerGraph(Network):

    def __init__(self):
        super().__init__()

    def find_shortest_path(self) -> Path:
        pass

    def add_link(self, src: Server, dst: Server) -> Link:
        return super().add_link(src, dst)
