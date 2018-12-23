from tokenize import String
from typing import List

from modelling.exceptions.modelling_exception import PathError, FlowError
from nc_arrivals.arrival import Arrival
from modelling.network.flow.path import Path
from modelling.network.link.link import Link
from modelling.network.server.server import Server


class Flow(object):
    alias: String
    arrival: Arrival
    path: Path

    def __init__(self, alias: String, arrival: Arrival, path: Path):
        self.alias = alias
        self.arrival = arrival
        self.path = path

    def get_servers(self) -> List[Server]:
        return self.path.get_servers()

    def get_links(self) -> List[Link]:
        return self.path.get_links()

    def get_source(self):
        try:
            return self.path.get_source()
        except PathError as error:
            raise FlowError(self, error.message)

    def __str__(self):
        return "[" + self.alias + ": " + self.arrival.__str__() + "; " + self.path.__str__() + "]"

    def __repr__(self):
        return "[" + self.alias + ": " + self.arrival.__repr__() + "; " + self.path.__repr__() + "]"
