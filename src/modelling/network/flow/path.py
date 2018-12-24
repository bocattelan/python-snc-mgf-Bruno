from typing import List

from modelling.exceptions.modelling_exception import PathError
from modelling.network.link.link import Link
from modelling.network.server.server import Server


class Path(object):

    def __init__(self, servers: List[Server], links: List[Link]):
        self.__servers = servers
        self.__links = links

    @property
    def servers(self) -> List[Server]:
        return self.__servers

    @property
    def links(self) -> List[Link]:
        return self.__links

    @property
    def source(self) -> Server:
        if len(self.servers) != 0:
            return self.servers[0]
        else:
            raise PathError(self, "Path is empty")

    @property
    def sink(self) -> Server:
        if len(self.servers) != 0:
            return self.servers[len(self.servers)-1]
        else:
            raise PathError(self, "Path is empty")

    def __str__(self):
        return "[path from: " + self.source.__str__() + " to " + self.sink.__str__() + "]"

    def __repr__(self):
        return "[" + ','.join(s.__str__() for s in self.servers) + "]"
