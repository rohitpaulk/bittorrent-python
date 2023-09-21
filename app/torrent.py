import hashlib

from dataclasses import dataclass

from .bencode import decode, encode

@dataclass
class Torrent:
    raw_file_contents: bytes

    @classmethod
    def from_file(cls, file_path: str):
        return cls(open(file_path, "rb").read())

    @property
    def info_hash(self):
        return hashlib.sha1(encode(self._metainfo_dict["info"])).digest()

    @property
    def length_in_bytes(self):
        return self._metainfo_dict["info"]["length"]

    @property
    def piece_length_in_bytes(self):
        return self._metainfo_dict["info"]["piece length"]

    @property
    def piece_hashes(self):
        encoded_hashes = self._metainfo_dict["info"]["pieces"]
        return [encoded_hashes[i : i + 20] for i in range(0, len(encoded_hashes), 20)]

    @property
    def tracker_url(self):
        return self._metainfo_dict["announce"].decode()

    @property
    def _metainfo_dict(self):
        return decode(self.raw_file_contents)

