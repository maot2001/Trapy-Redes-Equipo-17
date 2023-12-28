import socket
import struct
#from utils import checksum


class PacketException(Exception):
    pass


class Packet:
    def __init__(self,
                 data=None,
                 src_port=0,
                 dest_port=0,
                 seq_number=0,
                 ack=0,
                 data_len=0,
                 flags=0,
                 window=0,
                 ):
        self.src_port = src_port
        self.dest_port = dest_port
        self.seq_number = seq_number
        self.ack = ack
        self.data_len = data_len
        self.flags = flags
        self.window = window
        self.checksum = 0
        self._max_size_data = 512
        self.data = data
        if data is None:
            self.data = bytearray(0)
        if len(self.data) > self._max_size_data:
            raise PacketException(f"Data size must not exceed {self._max_size_data} bytes")

        self._format = "!HHIIHHHH"
        self._padding_data()

    def _padding_data(self):
        padding = max(0, self._max_size_data - self.data_len)
        if padding:
            self.data += bytearray(padding)

    def build(self) -> bytes:
        self.checksum = 0
        packet = struct.pack(self._format,
                             self.src_port,
                             self.dest_port,
                             self.seq_number,
                             self.ack,
                             self.data_len,
                             self.flags,
                             self.window,
                             self.checksum
                             )
        packet += self.data
        self.checksum = (~checksum(packet)) & 0xffff
        packet = struct.pack(self._format,
                             self.src_port,
                             self.dest_port,
                             self.seq_number,
                             self.ack,
                             self.data_len,
                             self.flags,
                             self.window,
                             self.checksum
                             )
        packet += self.data
        return packet

    def unpack(self, packet: bytes) -> None:
        self.data = packet[20:20 + self._max_size_data]
        packet = packet[:20]
        info = struct.unpack(self._format, packet)
        self.src_port = info[0]
        self.dest_port = info[1]
        self.seq_number = info[2]
        self.ack = info[3]
        self.data_len = info[4]
        self.flags = info[5]
        self.window = info[6]
        self.checksum = info[7]
def checksum(packet: bytes) -> int:
    bit_sum = 0
    for i in range(0, len(packet), 2):
        bit_sum += int.from_bytes(packet[i:i + 2], byteorder='big')
        bit_sum = (bit_sum >> 16) + (bit_sum & 0xffff)
    return bit_sum