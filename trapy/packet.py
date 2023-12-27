import array
import socket
from struct import pack, unpack


def create_flags(ack = False, syn = False, end = False, last_pack = False):
    flags = 0

    flags += 0b00010000 if ack else 0b00000000
    flags += 0b00000010 if syn else 0b00000000
    flags += 0b00000001 if end else 0b00000000
    flags += 0b00000100 if last_pack else 0b00000000

    return flags


def create_send_packet(conn, seq_num, ack, data):
    flags = create_flags(ack=False, syn=True)
    packet = Packet(conn.source_port, conn.dest_port, seq_num, ack, conn.source_ip, conn.dest_ip, flags, data)
    packet = packet.pack()
    return packet

def create_last_send_packet(conn, seq_num, ack, data):
    flags = create_flags(ack=False, syn=True, end = False, last_pack = True)
    packet = Packet(conn.source_port, conn.dest_port, seq_num, ack, conn.source_ip, conn.dest_ip, flags, data)
    packet = packet.pack()
    return packet


def my_unpack(packed_data):
    ipHeader = packed_data[0:20]
    tcpHeader = packed_data[20:38]
    body = packed_data[38:]

    pack = Packet()
    pack.source_ip = socket.inet_ntoa(ipHeader[12:16])
    pack.dest_ip = socket.inet_ntoa(ipHeader[16:20])
    pack.source_port, pack.dest_port, pack.seq_num, pack.ack, pack.flags, _, pack.data_len, pack.checksum = unpack("!HHLLbbHH", tcpHeader)
    pack.data = body
    return pack

def get_checksum(data : bytes):
    sum = 0
    if len(data)%2 > 0:
        data.append(b'0')
    for index in range(0,len(data),2):
        word = (data[index] << 8) + (data[index+1])
        sum = sum + word

    sum = (sum >> 16) + (sum & 0xffff)
    sum = ~sum & 0xffff

    return sum

class Packet:
    def __init__(self,
                 source_port=0,
                 dest_port=0,
                 seq_num=0,
                 ack=0,
                 source_ip='',
                 dest_ip='',
                 flags=0,
                 data: bytes = b''):
        self.source_port = source_port 
        self.dest_port = dest_port
        self.seq_num = seq_num
        self.ack = ack
        self.data_len = len(data)
        self.data = data
        if not len(self.data) % 2 == 0:
            self.data += b'0'
        self.checksum = 0
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.flags = flags

    def build_ip_header(self):
        ip_header = b'\x45\x00\x00\x28'  # Version, IHL, Type of Service | Total Length
        ip_header += b'\xab\xcd\x00\x00'  # Identification | Flags, Fragment Offset
        ip_header += b'\x40\x06\xa6\xec'  # TTL, Protocol | Header Checksum
        ip_header += socket.inet_aton(self.source_ip)  # Source Address
        ip_header += socket.inet_aton(self.dest_ip)  # Destination Address

        return ip_header

    def build_tcp_header(self):
        tcp_header = pack('!HH', self.source_port,
                          self.dest_port)  # Source Port | Destination Port
        tcp_header += pack('!L', self.seq_num)  # Sequence Number
        tcp_header += pack('!L', self.ack)  # Acknowledgement Number
        tcp_header += pack('!bb', self.flags, 0)  # Flags | Unused
        tcp_header += pack('!H', self.data_len)  # Data Lenght

        self.checksum = get_checksum(tcp_header + self.data)
        tcp_header += pack('!H', self.checksum)  # Checksum

        return tcp_header

    def build_tcp_header_no_checksum(self):
        tcp_header = pack('!HH', self.source_port,
                            self.dest_port)  # Source Port | Destination Port
        tcp_header += pack('!L', self.seq_num)  # Sequence Number
        tcp_header += pack('!L', self.ack)  # Acknowledgement Number
        tcp_header += pack('!bb', self.flags, 0)  # Flags | Unused
        tcp_header += pack('!H', self.data_len)  # Data Lenght

        return tcp_header

    def pack(self, packet_flag = '')-> bytes: 
        return self.build_ip_header() + self.build_tcp_header() + self.data

    def is_ack(self):
        is_ack = ((self.flags >> 4) & 1) == 1
        return (is_ack)

    def is_syn(self):
        is_syn = ((self.flags >> 1) & 1) == 1
        return(is_syn)

    def is_end(self):
        is_end = ((self.flags) & 1) == 1
        return(is_end)

    def is_last_pack(self):
        is_last = ((self.flags >> 2) & 1) == 1
        return is_last
    
    def check_checksum(self):
        return (get_checksum(self.build_ip_header() + self.build_tcp_header_no_checksum() + self.data) == self.checksum)