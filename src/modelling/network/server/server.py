from tokenize import String

from src.nc_service.service import Service


class Server(object):
    service: Service
    alias: String

    def __init__(self, alias: String, service: Service):
        self.alias = alias
        self.service = service

    def get_service(self):
        return self.service

    def __str__(self):
        return "[" + self.alias + "," + self.service.__str__() + "]"
