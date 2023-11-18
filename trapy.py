import logging
import socket
from utils import parse_address

logger = logging.getLogger(__name__)

class Conn:
    def __init__(self, sock = None):
        if (sock == None):
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        self.socket = sock

class ConnException(Exception):
    pass


def listen(address: str) -> Conn:
    conn = Conn()
    host, port = parse_address(address)

    logger.info(f'socket binded to {address}')
    conn.socket.bind((host, port))
    conn.socket.listen(1)

    return conn


def accept(conn) -> Conn:
    pass


def dial(address) -> Conn:
    pass


def send(conn: Conn, data: bytes) -> int:
    pass


def recv(conn: Conn, length: int) -> bytes:
    pass


def close(conn: Conn):
    pass


listen("127.0.0.1:8000")