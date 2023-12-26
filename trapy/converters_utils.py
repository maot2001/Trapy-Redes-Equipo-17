


def parse_address(address):
    host, port = address.split(':')

    if host == '':
        host = 'localhost'

    return host, int(port)


def str_to_bytes(value:str)->bytes:
   return value.encode('utf-8')


def bytes_to_int(b:bytes):
    return int.from_bytes(b, "big")


def int_to_bytes(number, size:int)->bytes:
    """
    Converts an integer to a byte array of specified size.

    Args:
        number (int): The integer to convert.
        size (int): The size of the resulting byte array.

    Returns:
        bytes: The byte array representation of the integer.
    """
    return number.to_bytes((size), "big")





def calculate_checksum(header:bytes) -> bytes:
    checksum = 0
    for i in range(int(len(header)/2)):
        header_16b = header[i*2:(i*2)+2]
        header_num = int.from_bytes(header_16b, "big")
        checksum += header_num

    while checksum > (2**16 - 1):
        checksum_bytes = checksum.to_bytes(4, "big")
        carry_bytes, checksum_bytes = checksum_bytes[0:2], checksum_bytes[2:4]
        carry, checksum = int.from_bytes(carry_bytes, "big"), int.from_bytes(checksum_bytes, "big")
        checksum += carry

    return (~checksum + 2**16).to_bytes(2, "big")
