import socket
import os
from typing import Tuple, Any, Optional
import random
from trapy.packet import Packet  # ,IPPacket
from trapy.timer import Timer
from trapy.utils import *
import logging

logger = logging.getLogger(__name__)
Address = Tuple[str, int]
path = "ports.trapy"
class Conn:
    def __init__(self):
        self.is_close = False
        self.__socket = socket.socket(socket.AF_INET,
                                      socket.SOCK_RAW,
                                      socket.IPPROTO_TCP)
        self.__socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        self.duration = 30

        self.N: int = 1
        self.send_base: int = 0
        self.send_base_sequence_number: int = 1

        self.recv_sequence_number: int = 0
        self.buffer: bytes = b''

        # bufsize =  ip_header + my_protocol_header + data
        self.max_data_packet = 512
        self.__default_bufsize: int = 20 + 20 + self.max_data_packet
        self.__dest_address: Optional[Address] = None
        self.__port: int = 0
        self.__host: str = ''
        self.__set_timeout(3)

    def __set_timeout(self, interval: float) -> None:
        self.__socket.settimeout(interval)

    def get_port(self) -> int:
        return self.__port

    def get_dest_address(self) -> Address:
        if self.__dest_address is None:
            raise ConnException("Destination address is not set")
        return self.__dest_address

    def set_dest(self, address: Address) -> None:
        self.__dest_address = address

    def close(self) -> None:
        self.N: int = 4
        self.send_base: int = 0

        self.recv_sequence_number: int = 0
        self.buffer: bytes = b''

        self.__dest_address: Optional[Address] = None
        self.__port: int = 0
        self.__host: str = ''

        self.is_close = True

    def bind(self, address: Address = None) -> None:
        if address is None:
            address = ('', get_free_port(path))
        #
        # if os.path.exists(path):
        #     file = open(path, 'r')
        #     lines = file.readlines()
        #     used_ports = list(map(int, lines[0].split()))
        #     if address[1] in used_ports:
        #         raise ConnException(f"Port {address[1]} in use")
        #     file.close()
        #     file = open('ports.trapy', 'a')
        #     file.write(f"{address[1]} ")
        # else:
        #     file = open('ports.trapy', 'w')
        #     file.write(f"{address[1]} ")
        self.__port = address[1]
        self.__host = address[0]
        # file.close()
        logger.info(f'socket binded to address {address}')

    def recv(self, timeout=0.5) -> Tuple[Optional[Packet], Any]:
        packet = Packet()
        address = ('', 0)
        self.__set_timeout(timeout)
        timer = Timer(timeout)
        timer.start()
        while True:
            try:
                data2, address = self.__socket.recvfrom(self.__default_bufsize)
                data = data2[20:]
                # print(f"Data recv: {data2}")
                packet.unpack(data)
                # print(f"Data recv: {data2}")
            except socket.timeout:
                timeout = timeout - timer.time()

            if packet.dest_port == self.__port:
                return packet, address

            if timer.timeout():
                return None, None
            self.__set_timeout(timeout)

    def send(self, data: bytes) -> int:
        if self.__dest_address is None:
            raise ConnException("Destination address is not set")
        data = make_ip_header(self.__dest_address[0]) + data
        # print(f'Data Send: {data}')
        # ip = IPPacket(src='10.0.0.1', dst=self.__dest_address[0])
        # ip_header = ip.assemble_ipv4_fields()
        # data = ip_header + data
        return self.__socket.sendto(data, self.__dest_address)


class ConnException(Exception):
    pass