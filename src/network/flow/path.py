from typing import List

from network.link.link import Link
from network.server.server import Server


class Path(object):
    servers: List[Server]
    links: List[Link]
    
    def __init__(self, servers: List[Server]):
        self.servers = servers