import socket
import struct

from dataclasses import dataclass


@dataclass
class Peer:
    ip: str
    port: int

    @classmethod
    def from_bytes(cls, bytes: bytes):
        ip_bytes, port_bytes = struct.unpack("!4s2s", bytes)
        ip = socket.inet_ntoa(ip_bytes)
        port = int.from_bytes(port_bytes, byteorder="big")
        return Peer(ip, port)

    @classmethod
    def list_from_bytes(cls, bytes: bytes):
        peers = []

        for i in range(0, len(bytes), 6):
            peers.append(cls.from_bytes(bytes[i : i + 6]))

        return peers
