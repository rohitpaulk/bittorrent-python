import io
import json
import sys

# import bencodepy - available if you need it!
# import requests - available if you need it!


def do_decode(bencoded_str_io):
    first_byte = bencoded_str_io.read(1)

    if first_byte.isdigit():
        length_str = first_byte

        while True:
            byte = bencoded_str_io.read(1)
            if byte == b":":
                break
            length_str += byte

        length = int(length_str)
        return bencoded_str_io.read(length)
    elif first_byte == b"i":
        integer_str = b""

        while True:
            byte = bencoded_str_io.read(1)
            if byte == b"e":
                break
            integer_str += byte

        return int(integer_str)
    elif first_byte == b"l":
        values = []

        while bencoded_str_io.peek(1) != b"e":
            values.append(do_decode(bencoded_str_io))

        assert bencoded_str_io.read(1) == b"e" # consume the "e"

        return values
    elif first_byte == b"d":
        keys = []
        values = []

        while bencoded_str_io.peek(1) != b"e":
            keys.append(do_decode(bencoded_str_io).decode())
            values.append(do_decode(bencoded_str_io))

        assert bencoded_str_io.read(1) == b"e" # consume the "e"

        return dict(zip(keys, values))
    else:
        raise NotImplementedError(f"Unhandled first_char: {first_byte}")


# Examples:
#
# - decode_bencode("5:hello") -> "hello"
# - decode_bencode("10:hello12345") -> "hello12345"
def decode(bencoded_value):
    bencoded_str_io = io.BufferedReader(io.BytesIO(bencoded_value))

    return do_decode(bencoded_str_io)


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
    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
