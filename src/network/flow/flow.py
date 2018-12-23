from tokenize import String
from typing import List

from nc_arrivals.arrival import Arrival
from network.flow.path import Path
from network.server.server import Server


class Flow(object):
    alias: String
    arrival: Arrival
    path: Path

    def __init__(self, alias: String, arrival: Arrival, servers: List[Server]):
        self.alias = alias
        self.arrival = arrival
        self.path = Path(servers)
