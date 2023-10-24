import socket
import struct

from dataclasses import dataclass

from .torrent import Torrent


class Handshake:
    info_hash: bytes
    peer_id: bytes

    def __init__(self, info_hash: bytes, peer_id: bytes):
        self.info_hash = info_hash
        self.peer_id = peer_id

    def to_bytes(self):
        pstrlen = b"\x13"
        pstr = b"BitTorrent protocol"
        reserved = b"\x00\x00\x00\x00\x00\x00\x00\x00"

        return pstrlen + pstr + reserved + self.info_hash + self.peer_id

    @classmethod
    def from_bytes(cls, bytes: bytes):
        # Using just [0] returns an int, use [0:1] to get a bytes object
        pstrlen = bytes[0:1]

        if pstrlen != b"\x13":
            raise ValueError(f"pstrlen must be 19, got {repr(pstrlen)}")

        pstr = bytes[1:20]

        if pstr != b"BitTorrent protocol":
            raise ValueError(f"pstr must be b'BitTorrent protocol', got {pstr}")

        info_hash = bytes[28:48]
        peer_id = bytes[48:68]

        return cls(info_hash, peer_id)


@dataclass
class Peer:
    ip: str
    port: int

    _socket: socket.socket = None

    @classmethod
    def from_str(cls, string: str):
        ip, port = string.split(":")
        return cls(ip, int(port))

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

    def connect(self):
        if self._socket:
            raise RuntimeError("Already connected")

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.ip, self.port))

    def handshake(self, torrent: Torrent) -> Handshake:
        outgoing_handshake = Handshake(torrent.info_hash, b"00112233445566778899")
        self._socket.send(outgoing_handshake.to_bytes())

        response = self._socket.recv(1024)
        incoming_handshake = Handshake.from_bytes(response)

        if incoming_handshake.info_hash != torrent.info_hash:
            raise ValueError(
                f"Expected info hash {torrent.info_hash}, got {incoming_handshake.info_hash}"
            )

        return incoming_handshake
