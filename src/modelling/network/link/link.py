from modelling.network.server.server import Server


class Link(object):

    def __init__(self, src: Server, dst: Server):
        self.__src = src
        self.__dst = dst

    @property
    def src(self) -> Server:
        return self.__src

    @property
    def dst(self) -> Server:
        return self.__dst

    def __str__(self):
        return "[link:" + self.__src.alias + ", " + self.__dst.alias + "]"
