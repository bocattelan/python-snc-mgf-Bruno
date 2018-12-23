from typing import List

from modelling.exceptions.modelling_exception import PathError
from modelling.network.link.link import Link
from modelling.network.server.server import Server


class Path(object):
    servers: List[Server]
    links: List[Link]

    def __init__(self, servers: List[Server], links: List[Link]):
        self.servers = servers
        self.links = links

    def get_servers(self) -> List[Server]:
        return self.servers

    def get_links(self) -> List[Link]:
        return self.links

    def get_source(self):
        if len(self.servers) != 0:
            return self.servers[0]
        else:
            raise PathError(self, "Path is empty")

    def get_sink(self):
        if len(self.servers) != 0:
            return self.servers[len(self.servers)]
        else:
            raise PathError(self, "Path is empty")

    def __str__(self):
        return "[path from: " + self.get_source().__str__() + " to " + self.get_sink().__str__() + "]"

    def __repr__(self):
        return "[" + ','.join(s.__str__() for s in self.servers) + "]"
