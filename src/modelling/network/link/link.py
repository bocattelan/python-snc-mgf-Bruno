from modelling.exceptions.modelling_exception import LinkError
from modelling.network.server.server import Server
from nc_service.service import Service


class Link(object):

    def __init__(self, src: Server, dst: Server, service=None):
        self.__src = src
        self.__dst = dst
        if not(service is None) and not(issubclass(service.__class__, Service)):
            raise LinkError(src, dst, "Invalid service for network graph link:" + service.__str__())
        self.__service = service

    @property
    def src(self) -> Server:
        return self.__src

    @property
    def dst(self) -> Server:
        return self.__dst

    def is_turn(self) -> bool:
        return self.__service is None

    @property
    def service(self):
        return self.__service

    def __str__(self):
        return "[link:" + self.__src.alias + ", " + self.__dst.alias + "]"
