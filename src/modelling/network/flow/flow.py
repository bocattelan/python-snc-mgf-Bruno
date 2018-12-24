from tokenize import String
from typing import List

from modelling.exceptions.modelling_exception import PathError, FlowError
from nc_arrivals.arrival import Arrival
from modelling.network.flow.path import Path
from modelling.network.link.link import Link
from modelling.network.server.server import Server


class Flow(object):

    def __init__(self, alias: String, arrival: Arrival, path: Path):
        self.__alias = alias
        self.__arrival = arrival
        self.__path = path

    @property
    def alias(self) -> String:
        return self.__alias

    @property
    def arrival(self) -> Arrival:
        return self.__arrival

    @property
    def servers(self) -> List[Server]:
        return self.__path.servers

    @property
    def links(self) -> List[Link]:
        return self.__path.links

    @property
    def source(self) -> Server:
        try:
            return self.__path.source
        except PathError as error:
            raise FlowError(self, error.message)

    @property
    def sink(self) -> Server:
        try:
            return self.__path.sink
        except PathError as error:
            raise FlowError(self, error.message)

    def __str__(self):
        return "[" + self.alias + ": " + self.__arrival.__str__() + "; " + self.__path.__str__() + "]"

    def __repr__(self):
        return "[" + self.alias + ": " + self.__arrival.__repr__() + "; " + self.__path.__repr__() + "]"
