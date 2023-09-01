import io


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

        while chr(bencoded_str_io.peek(1)[0]) != "e":
            values.append(do_decode(bencoded_str_io))

        assert bencoded_str_io.read(1) == b"e"  # consume the "e"

        return values
    elif first_byte == b"d":
        keys = []
        values = []

        while chr(bencoded_str_io.peek(1)[0]) != "e":
            keys.append(do_decode(bencoded_str_io).decode())
            values.append(do_decode(bencoded_str_io))

        assert bencoded_str_io.read(1) == b"e"  # consume the "e"

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


def encode(value):
    if isinstance(value, str):
        return f"{len(value)}:{value}".encode()
    if isinstance(value, bytes):
        return b"".join(len(value), b":", value)
    elif isinstance(value, int):
        return f"i{value}e".encode()
    elif isinstance(value, list):
        encoded_list = b"".join(encode(item) for item in value)
        return b"l" + encoded_list + b"e"
    elif isinstance(value, dict):
        encoded_dict = b"".join(
            encode(key) + encode(value[key]) for key in sorted(value.keys())
        )
        return b"d" + encoded_dict + b"e"
    else:
        raise TypeError(f"Type not serializable: {type(value)}")
