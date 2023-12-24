import logging
import time
from utils import *
from conn import *

logger = logging.getLogger(__name__)


def listen(address: str):
    conn = Conn()
    conn.origin_address = parse_address(address)

    conn.socket.bind(conn.origin_address)
    logger.info(f'socket binded to {address}')

    conn.socket.listen(10)

    return conn


def accept(conn: Conn):
    conn.start()

    while True:
        try:
            address, protocol, _ = data_conn(conn)
        except:
            continue

        if not protocol[14] == 1 or get_bytes(protocol, 8, 12) != 1:
            continue

        logger.info(f'syn recived')
        conn.time_init = conn.time_stop

        accept_conn = Conn()

        accept_conn.origin_address = conn.origin_address
        accept_conn.connected_address = address

        accept_conn.ack = get_bytes(protocol, 4, 8) + 1

        packet = create_packet(accept_conn, ACK=1, SYN=1)

        conn.start()

        logger.info(f'syn-ack sending')
        accept_conn.socket.sendto(packet, accept_conn.connected_address)

        while True:
            if not accept_conn.running() or accept_conn.timeout():
                logger.warning(f'syn-ack sending again')
                accept_conn.socket.sendto(packet, accept_conn.connected_address)
                accept_conn.origin_address = conn.origin_address

            if accept_conn.waiter(180):
                accept_conn.time_init = accept_conn.time_stop
                logger.error(f'error sending')
                raise ConnException()

            try:
                address, protocol, _ = data_conn(accept_conn)
            except:
                continue

            if get_bytes(protocol, 4, 8) != accept_conn.ack or get_bytes(protocol, 8, 12) != accept_conn.seq + 1 or not \
            protocol[17] == 1:
                continue

            logger.info(f'ack recived')
            accept_conn.seq = get_bytes(protocol, 8, 12)
            accept_conn.ack = get_bytes(protocol, 4, 8) + 1
            conn.time_init = conn.time_stop
            return accept_conn


def dial(address: str):
    conn = Conn()
    conn.origin_address = conn.socket.getsockname()
    conn.connected_address = parse_address(address)
    conn.ack = 1

    packet = create_packet(conn,SYN =1)

    conn.start()
    logger.info(f'syn sending')
    conn.socket.sendto(packet, conn.connected_address)

    while True:
        if not conn.running() or conn.timeout():
            logger.warning(f'syn sending again')
            conn.socket.sendto(packet, conn.connected_address)
            conn.origin_address = conn.socket.getsockname()
            conn.time_init =  time.time()
            
        if conn.waiter(180):
            conn.time_init = conn.time_stop
            logger.error(f'error sending')
            raise ConnException()
        
        try:
            address, protocol, _ = data_conn(conn)
        except:
            continue
        
        if protocol[17] == 1 and protocol[14] == 1 and get_bytes(protocol, 8, 12) == conn.seq + 1:
            logger.info(f'syn-ack recived')
            conn.seq = get_bytes(protocol, 8, 12)
            conn.ack = get_bytes(protocol, 4, 8) + 1
            conn.connected_address = address
            conn.origin_address = conn.socket.getsockname()

            logger.info(f'ack sending')
            packet = create_packet(conn, ACK=1)
            conn.socket.sendto(packet, conn.connected_address)
            break
    conn.time_init = conn.time_stop
    return conn

def send(conn: Conn, data: bytes) -> int:
    pass


def recv(conn: Conn, length: int) -> bytes:
    pass


def close(conn: Conn):
    pass


listen("127.0.0.1:8000")
