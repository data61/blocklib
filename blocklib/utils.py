import base64
from bitarray import bitarray
from typing import Sequence, Any


def deserialize_bitarray(bytes_data: Any):
    ba = bitarray(endian='big')
    data_as_bytes = base64.decodebytes(bytes_data.encode())
    ba.frombytes(data_as_bytes)
    return ba


def deserialize_filters(filters: Sequence[Any]):
    res = []
    for i, f in enumerate(filters):
        ba = deserialize_bitarray(f)
        res.append(ba)
    return res

