import socket
import random

class Conn:

    def __init__(self, sock=None):
        self.origin_address: tuple[str, int] = None

        self.connected_address: list(tuple[str, int]) = []
        self.ack: list(bytes) = []
        self.seq: list(bytes) = []
        
        self.windows_length = 4

        if sock == None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.socket = sock

    def refresh(self, index: int, new_ack: int, new_seq: int, data: int):
        self.seq[index] = new_ack.to_bytes(4,byteorder='big', signed=False)
        new_seq += data
        self.ack[index] = new_seq.to_bytes(4,byteorder='big', signed=False)

    def bind(self, address = None) -> None:
        if address is None:
            while True:
                try:
                    ip_r = random.randint(11, 254)
                    port_r = random.randint(4000, 8000)
                    address = ("127.68.0." + str(ip_r), port_r)
                    self.socket.bind(address)
                except:
                    continue
                break
        else:
            self.socket.bind(address)

class ConnException(Exception):
    pass