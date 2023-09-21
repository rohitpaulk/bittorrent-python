import hashlib
import json
import sys
import socket

from dataclasses import dataclass

# import bencodepy - available if you need it!
import requests

from .bencode import decode, encode
from .peer import Peer
from .torrent import Torrent


def main():
    command = sys.argv[1]

    if command == "decode":
        bencoded_value = sys.argv[2].encode()

        # json.dumps() can't handle bytes, but bencoded "strings" need to be
        # bytestrings since they might contain non utf-8 characters.
        #
        # Let's convert them to strings for printing to the console.
        def bytes_to_str(data):
            if isinstance(data, bytes):
                return data.decode()

            raise TypeError(f"Type not serializable: {type(data)}")

        print(json.dumps(decode(bencoded_value), default=bytes_to_str))
    elif command == "info":
        torrent_file_path = sys.argv[2]
        torrent = Torrent.from_file(torrent_file_path)

        print(f"Tracker URL: {torrent.tracker_url}")
        print(f"Length: {torrent.length_in_bytes}")
        print(f"Info Hash: {torrent.info_hash.hex()}")
        print(f"Piece Length: {torrent.piece_length_in_bytes}")

        print("Piece Hashes:")
        for piece_hash in torrent.piece_hashes:
            print(piece_hash.hex())
    elif command == "peers":
        torrent_file_path = sys.argv[2]
        torrent = Torrent.from_file(torrent_file_path)

        response = requests.get(
            torrent.tracker_url,
            params={
                "info_hash": torrent.info_hash,
                "peer_id": "00112233445566778899",
                "port": "6881",
                "uploaded": "0",
                "downloaded": "0",
                "left": torrent.length_in_bytes,
                "compact": "1",
            },
        )

        response_dict = decode(response.content)

        encoded_peers = response_dict["peers"]
        peers = Peer.list_from_bytes(response_dict["peers"])
        for peer in peers:
            print(f"{peer.ip}:{peer.port}")
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
