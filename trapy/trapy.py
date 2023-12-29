import logging
import time
import random
import threading
from utils import *
from conn import *
from timer import Timer
from _send import send as sends

logger = logging.getLogger(__name__)

def listen(address: str):
    conn = Conn()

    conn.origin_address = parse_address(address)

    conn.bind(conn.origin_address)
    logger.info(f'socket binded to {address}')

    return conn

def accept(conn: Conn):

    while True:
        try:
            packet, _ = conn.socket.recvfrom(1024)
            address, protocol, _, flags = data_conn(packet)
        except:
            continue

        if flags.SYN == 0:
            continue
        
        if address in conn.connected_address:
            logger.error(f'existing connection with {address}')
            continue

        logger.info(f'syn received from {address}')

        conn.connected_address.append(address)
        
        seq = int.from_bytes(protocol[4:8], byteorder='big', signed=False)
        seq += 1
        conn.ack.append(seq.to_bytes(4,byteorder='big', signed=False))

        tmp = random.randint(2, 1e6)
        conn.seq.append(tmp.to_bytes(4,byteorder='big',signed=False))
        
        flags = Flags()
        flags.ACK = 1
        flags.SYN = 1

        index = conn.connected_address.index(address)
        packet = create_packet(conn, index, flags)

        logger.info(f'syn-ack sending')
        conn.socket.sendto(packet, conn.connected_address[index])

        while True:
            """if not accept_conn.running() or accept_conn.timeout():
                logger.warning(f'syn-ack sending again')
                accept_conn.socket.sendto(packet, accept_conn.connected_address)
                accept_conn.origin_address = conn.origin_address

            if accept_conn.waiter(180):
                accept_conn.stop()
                logger.error(f'error sending')
                raise ConnException()"""

            try:
                packet, _ = conn.socket.recvfrom(1024)
                address, protocol, _, flags = data_conn(packet)
            except:
                continue

            ack = int.from_bytes(conn.seq[index], byteorder='big', signed=False)
            ack += 1
            if protocol[4:8] != conn.ack[index] or protocol[8:12] != ack.to_bytes(4,byteorder='big', signed=False) or flags.ACK == 0:
                continue

            logger.info(f'ack received')
            conn.refresh(index, int.from_bytes(protocol[8:12], byteorder='big', signed=False), int.from_bytes(protocol[4:8], byteorder='big', signed=False), 0)
            return conn

def dial(address: str) -> Conn:
    address = parse_address(address)
    conn = Conn()
    conn.bind() 
    conn.origin_address = conn.socket.getsockname()

    conn.connected_address.append(address)

    conn.ack.append(int(0).to_bytes(4,byteorder='big',signed=False))
    tmp = random.randint(2, 1e6)
    conn.seq.append(tmp.to_bytes(4,byteorder='big',signed=False))

    flags = Flags()
    flags.SYN = 1

    index = conn.connected_address.index(address)
    packet = create_packet(conn, index, flags)

    logger.info(f'syn sending')
    conn.socket.sendto(packet, conn.connected_address[index])

    while True:
        """if not conn.running() or conn.timeout():
            logger.warning(f'syn sending again')
            conn.socket.sendto(packet, conn.connected_address)
            conn.origin_address = conn.socket.getsockname()
            conn.time_init = time.time()
            
        if conn.waiter(180):
            conn.stop()
            logger.error(f'error sending')
            #TODO: Poner la exepcionraise ConnException()"""
        
        try:
            packet, _ = conn.socket.recvfrom(1024)
            address, protocol, _, flags = data_conn(packet)
        except:
            continue
        
        ack = int.from_bytes(conn.seq[index], byteorder='big', signed=False)
        ack += 1
        if flags.ACK == 0 or flags.SYN == 0 or protocol[8:12] != ack.to_bytes(4,byteorder='big', signed=False):
            continue

        logger.info(f'syn-ack received')
        conn.refresh(index, int.from_bytes(protocol[8:12], byteorder='big', signed=False), int.from_bytes(protocol[4:8], byteorder='big', signed=False), 1)

        flags = Flags()
        flags.ACK = 1
        
        packet = create_packet(conn, index, flags)
        
        logger.info(f'ack sending')
        conn.socket.sendto(packet, conn.connected_address[index])
        break
    return conn

def send(conn: Conn, data: bytes) -> int:
    mss: int = 1024
    data_len = len(data)
    flags = Flags()
    packet = create_packet(conn, 0, flags, data)
    conn.socket.sendto(packet, conn.connected_address[0])

    while True:
        try:
            packet, _ = conn.socket.recvfrom(mss)
            address, protocol, data, flags = data_conn(packet)
        except:
            continue

        if address != conn.connected_address[0]:
            continue

        tcp_header = Protocol_Wrapped(protocol)
        seq = convert_bytes_to_int(conn.seq[0])
        seq += data_len
        rec_ack = convert_bytes_to_int(tcp_header.ack_num)
        
        time.sleep(5)
        if flags.ACK == 0 or seq != rec_ack:
            continue
        
        break
    return data_len

def recv(conn: Conn, length: int) -> bytes:
    data = 0
    while True:
        try:
            packet, _ = conn.socket.recvfrom(length)
            address, protocol, data, flags = data_conn(packet)
        except:
            continue

        if not address in conn.connected_address:
            continue

        index = conn.connected_address.index(address)
        if flags.SYN == 1 or flags.ACK == 1 or flags.FIN == 1 or flags.RST == 1:
            continue

        tcp_header = Protocol_Wrapped(protocol)
        rec_ack = tcp_header.ack_num
        
        if conn.seq[index] != rec_ack:
            continue
        
        ack = convert_bytes_to_int(conn.ack[index])
        ack += len(data)
        conn.ack[index] = ack.to_bytes(4, byteorder='big', signed=False)
        flags = Flags()
        flags.ACK = 1
        packet = create_packet(conn, index, flags)
        conn.socket.sendto(packet, conn.connected_address[index])
        break
    return data

def close(conn: Conn):
    conn.socket.close()
    logger.info(f'close connection')
    conn.socket = None
