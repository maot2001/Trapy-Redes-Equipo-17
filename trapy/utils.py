from conn import *


def parse_address(address):
    host, port = address.split(':')

    if host == '':
        host = 'localhost'

    return host, int(port)


def get_bytes(protocol, init, end):
    return int.from_bytes(protocol[init:end], byteorder='big', signed=False)


def build_iph(origin_ip, connected_ip):
    ip_header = b'\x45\x00\x00\x28'  # Version, IHL, Type of Service | Total Length
    ip_header += b'\xab\xcd\x00\x00'  # Identification | Flags, Fragment Offset
    ip_header += b'\x40\x06\xa6\xec'  # TTL, Protocol | Header Checksum   xff en protocol
    origin_ip = [int(i) for i in origin_ip.split('.')]
    connected_ip = [int(i) for i in connected_ip.split('.')]
    ip_header += bytes(origin_ip)  # Source Address
    ip_header += bytes(connected_ip)  # Destination Address
    return ip_header


def build_protocolh(o_port, c_port, seq, ack, windows_length, ACK, SYN, FIN):
    tcp_header = o_port.to_bytes(2, byteorder='big', signed=False)  # Source Port
    tcp_header += c_port.to_bytes(2, byteorder='big', signed=False)  # Destination Port
    tcp_header += seq.to_bytes(4, byteorder='big', signed=False)  # Sequence Number
    tcp_header += ack.to_bytes(4, byteorder='big', signed=False)  # Acknowledgement Number
    tcp_header += ((ACK << 4) + (SYN << 1) + (FIN)).to_bytes(2, byteorder='big', signed=False)  # Flags
    tcp_header += windows_length.to_bytes(2, byteorder='big', signed=False)  # Window Size
    tcp_header += b'\x00\x00\x00\x00'  # Checksum | Urgent Pointer


def create_packet(conn, ACK=0, SYN=0, data=b''):
    o_addr, o_port = conn.origin_address
    c_addr, c_port = conn.connected_address

    ip_header = build_iph(o_addr, c_addr)
    protocol_header = build_protocolh(o_port, c_port, 0, conn.ack, conn.windows_length, ACK, SYN, 0)
    return ip_header + protocol_header


def data_conn(conn):
    try:
        packet, _ = conn.socket.recvfrom(1024)
    except:
        return None

    ip_header, protocol, data = packet[20:40], packet[40:60], packet[60:]
    ip = '.'.join(map(str, ip_header[12:16]))
    port = int.from_bytes(protocol[:2], byteorder='big', signed=False)

    return ((ip, port), protocol, data)
