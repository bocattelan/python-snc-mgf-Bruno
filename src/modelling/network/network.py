from tokenize import String
from typing import Set, Dict, List
from abc import ABC, abstractmethod

from modelling.exceptions.modelling_exception import LinkError, FlowCreationError
from nc_arrivals.arrival import Arrival
from nc_service.service import Service
from modelling.network.flow.flow import Flow
from modelling.network.flow.path import Path
from modelling.network.link.link import Link
from modelling.network.server.server import Server


class Network(ABC):

    def __init__(self):
        self.servers = set()
        self.flows = set()
        self.flows_per_server = dict()
        self.flows_per_link = dict()
        self.links_src = dict()
        self.links_dst = dict()
        self.source_flows = dict()

    def add_server(self, alias: String, service: Service) -> Server:
        server = Server(alias, service)
        self.servers.add(server)
        return server

    def get_servers(self) -> Set[Server]:
        return self.servers

    def get_flows(self) -> Set[Flow]:
        return self.flows

    def update_maps(self, flow: Flow):
        for server in flow.servers:
            if not (self.flows_per_server.__contains__(server)):
                self.flows_per_server[server] = set()
            self.flows_per_server[server].add(flow)

        for link in flow.links:
            if not (self.flows_per_link.__contains__(link)):
                self.flows_per_link[link] = set()
            self.flows_per_link[link].add(flow)

            if not (self.links_src.__contains__(link.src)):
                self.links_src[link.src] = set()
            self.links_src[link.src].add(link)

            if not (self.links_dst.__contains__(link.dst)):
                self.links_dst[link.dst] = set()
            self.links_dst[link.dst].add(link)
        pass

    def find_link(self, src: Server, dst: Server) -> Link:
        for link in self.links_src.get(src):
            if link.get_dst().__eq__(dst):
                return link
        raise LinkError(src, dst, "No link found")

    def __create_path(self, servers: List[Server]) -> Path:
        links = list()
        for i in range(len(servers) - 1):
            links.append(self.find_link(servers[i], servers[i + 1]))
        return Path(servers, links)

    def add_flow(self, alias: String, arrival: Arrival, servers: List[Server]) -> Flow:
        try:
            flow = Flow(alias, arrival, self.__create_path(servers))
        except LinkError as error:
            raise FlowCreationError(error.message + " from" + error.src + " to " + error.dst)

        if not (self.source_flows.__contains__(flow.source)):
            self.source_flows[flow.source] = set()
        self.source_flows[flow.source].add(flow)
        self.update_maps(flow)
        self.flows.add(flow)
        return flow

    @abstractmethod
    def add_link(self, src: Server, dst: Server) -> Link:
        link = Link(src, dst)
        self.links.add(link)
        return link

    @abstractmethod
    def find_shortest_path(self) -> List[Server]:
        pass

    def __str__(self):
        return "{" + type(self).__name__ + ":" + ';'.join(s.__str__() for s in self.servers) + "}"
