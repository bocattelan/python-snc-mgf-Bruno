from tokenize import String
from typing import Set, List
from abc import ABC, abstractmethod

from modelling.exceptions.modelling_exception import LinkError, FlowCreationError, FlowError
from nc_arrivals.arrival import Arrival
from nc_service.service import Service
from modelling.network.flow.flow import Flow
from modelling.network.flow.path import Path
from modelling.network.link.link import Link
from modelling.network.server.server import Server


class Network(ABC):

    def __init__(self):
        self.__servers = set()
        self.__links = set()
        self.__flows = set()
        self.__flows_per_server = dict()
        self.__flows_per_link = dict()
        self.__links_src = dict()
        self.__links_dst = dict()
        self.__source_flows = dict()

    @property
    def servers(self) -> Set[Server]:
        return self.__servers

    @property
    def links(self) -> Set[Link]:
        return self.__links

    @property
    def flows(self) -> Set[Flow]:
        return self.__flows

    @abstractmethod
    def add_link(self, src: Server, dst: Server, service) -> Link:
        link = Link(src, dst, service)
        if not (self.__links_src.__contains__(src)):
            self.__links_src[src] = set()
        self.__links_src[src].add(link)
        if not (self.__links_dst.__contains__(dst)):
            self.__links_dst[dst] = set()
        self.__links_dst[dst].add(link)

        self.__links.add(link)
        return link

    @abstractmethod
    def find_shortest_path(self, src: Server, dst: Server) -> List[Server]:
        pass

    def __update_maps_add(self, flow: Flow):
        for server in flow.servers:
            if not (self.__flows_per_server.__contains__(server)):
                self.__flows_per_server[server] = set()
            self.__flows_per_server[server].add(flow)

        for link in flow.links:
            if not (self.__flows_per_link.__contains__(link)):
                self.__flows_per_link[link] = set()
            self.__flows_per_link[link].add(flow)

            if not (self.__links_src.__contains__(link.src)):
                self.__links_src[link.src] = set()
            self.__links_src[link.src].add(link)

            if not (self.__links_dst.__contains__(link.dst)):
                self.__links_dst[link.dst] = set()
            self.__links_dst[link.dst].add(link)
        pass

    def __update_maps_remove(self, flow: Flow):
        for server in flow.servers:
            self.__flows_per_server[server].remove(flow)

        for link in flow.links:
            self.__flows_per_link[link].remove(flow)

            self.__links_src[link.src].remove(link)

            self.__links_dst[link.dst].remove(link)
        pass

    def find_link(self, src: Server, dst: Server) -> Link:
        for link in self.__links_src.get(src):
            if link.dst.__eq__(dst):
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

        if not (self.__source_flows.__contains__(flow.source)):
            self.__source_flows[flow.source] = set()
        self.__source_flows[flow.source].add(flow)
        self.__update_maps_add(flow)
        self.__flows.add(flow)
        return flow

    def remove_flow(self, flow: Flow):
        if not(self.__flows.__contains__(flow)):
            raise FlowError(flow, "Flow not present in network")
        self.__flows.remove(flow)
        self.__update_maps_remove(flow)

    def previous_servers(self, server: Server) -> Set[Server]:
        previous_servers = set()
        for link in self.__links_dst.get(server):
            previous_servers.add(link.src)
        return previous_servers

    def succeeding_servers(self, server: Server) -> Set[Server]:
        succeeding_servers = set()
        for link in self.__links_src.get(server):
            succeeding_servers.add(link.dst)
        return succeeding_servers

    def add_server(self, alias: String, service=None) -> Server:
        server = Server(alias, service)
        self.__servers.add(server)
        return server

    def __str__(self):
        return "{" + type(self).__name__ + ":" + ';'.join(s.__str__() for s in self.servers) + "}"
