from modelling.network.server.server import Server


class Link(object):
    src: Server
    dst: Server

    def __init__(self, src: Server, dst: Server):
        self.src = src
        self.dst = dst

    def get_src(self):
        return self.src

    def get_dst(self):
        return self.dst

    def __str__(self):
        return "[link:" + self.src.alias + ", " + self.dst.alias + "]"
