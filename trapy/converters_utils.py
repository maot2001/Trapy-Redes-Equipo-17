from trapy import TCP_Header, Flags


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


def Get_TCP_Header_From_IP_TCP_Headers(ip_header:bytes,tcp_header:bytes)->TCP_Header:
    """
    This function extracts TCP header information from IP and TCP headers.

    Parameters:
    ip_header (bytes): The IP header.
    tcp_header (bytes): The TCP header.

    Returns:
    TCP_Header: An object containing the extracted TCP header information.
    """
    #Ips address
    addr_source=ip_header[12:16]
    addr_dest=ip_header[16:20]
    #Ports
    source_port = tcp_header[0:2]
    dest_port = tcp_header[2:4]
    #seq and ack number
    secnumber = tcp_header[4:8]
    acknumber =tcp_header[8:12]

    #flags
    flags = Flags()
    flags.from_bytes_to_flags(tcp_header[13])

    #windows size
    recv_window = tcp_header[14:16]

    tcp_header=TCP_Header(source_address=addr_source,
                          destination_address=addr_dest,
                          port_source=source_port,
                          port_destination=dest_port,
                          seq_number=secnumber,
                          ack_number=acknumber,
                          flags=flags,
                          recv_window=recv_window)

    return tcp_header


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
