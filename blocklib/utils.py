import base64
from bitarray import bitarray
from typing import Sequence, Any, List


def check_header(header: List[str], row: Sequence[Any]):
    """Check if header is consistent with data dimension."""
    error_msg = f'There are {len(header)} features specified in header, but each row has {len(row)} fields'
    assert len(header) == len(row), error_msg


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

