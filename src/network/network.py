from tokenize import String
from typing import Set, Dict, List
from abc import ABC, abstractmethod

from nc_arrivals.arrival import Arrival
from nc_service.service import Service
from network.flow.flow import Flow
from network.flow.path import Path
from network.link.link import Link
from network.server.server import Server


class Network(ABC):
    servers: Set[Server]
    links: Set[Link]
    flows: Set[Flow]
    flows_per_server: Dict[Server, Set[Flow]]

    def __init__(self):
        self.servers = set()
        self.flows = set()
        self.flows_per_server = dict()

    def add_server(self, alias: String, service: Service) -> Server:
        server = Server(alias, service)
        self.servers.add(server)
        return server

    def get_servers(self) -> Set[Server]:
        return self.servers

    def add_flow(self, alias: String, arrival: Arrival, servers: List[Server]) -> Flow:
        flow = Flow(alias, arrival, servers)
        for server in servers:
            if self.flows_per_server.__contains__(server):
                self.flows_per_server[server].add(flow)
            else:
                self.flows_per_server[server] = set()
                self.flows_per_server[server].add(flow)
        return flow

    @abstractmethod
    def add_link(self, src: Server, dst: Server) -> Link:
        link = Link(src, dst)
        self.links.add(link)
        return link

    @abstractmethod
    def find_shortest_path(self) -> Path:
        pass

    def __str__(self):
        return "{" + type(self).__name__ + ":" + ';'.join(s.__str__() for s in self.servers) + "}"
