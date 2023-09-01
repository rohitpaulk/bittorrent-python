import hashlib
import json
import sys

# import bencodepy - available if you need it!
# import requests - available if you need it!

from .bencode import decode, encode


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
        torrent_file_contents = open(torrent_file_path, "rb").read()
        torrent_file_dict = decode(torrent_file_contents)
        info_hash = hashlib.sha1(encode(torrent_file_dict["info"])).hexdigest()
        piece_length = torrent_file_dict["info"]["piece length"]

        print(f"Tracker URL: {torrent_file_dict['announce'].decode()}")
        print(f"Length: {torrent_file_dict['info']['length']}")
        print(f"Info Hash: {info_hash}")
        print(f"Piece Length: {piece_length}")

        print("Piece Hashes:")
        for i in range(0, len(torrent_file_dict["info"]["pieces"]), 20):
            print(torrent_file_dict["info"]["pieces"][i : i + 20].hex())
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
