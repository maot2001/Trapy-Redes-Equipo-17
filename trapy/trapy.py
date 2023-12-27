import logging
import time
import random
import threading
from utils import *
from conn import *
from packet import *
from timer import Timer
from _send import send as sends
logger = logging.getLogger(__name__)

def listen(address: str):
    conn = Conn()

    conn.origin_address = parse_address(address)

    conn.socket.bind(conn.origin_address)
    logger.info(f'socket binded to {address}')

    return conn

def accept(conn: Conn):
    #conn.start()

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
        #conn.stop()

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

        #conn.start()

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
            #accept_conn.stop()
            return conn

def dial(address: str, clients) -> Conn:
    address = parse_address(address)
    #address_2 = parse_address("127.68.0.11:5010")
    conn = Conn()
    conn.socket.bind(('0.0.0.0', 0)) 
    conn.origin_address = conn.socket.getsockname()

    conn.connected_address.append(address)

    conn.ack.append(int(0).to_bytes(4,byteorder='big',signed=False))
    tmp = random.randint(2, 1e6)
    conn.seq.append(tmp.to_bytes(4,byteorder='big',signed=False))

    flags = Flags()
    flags.SYN = 1

    index = conn.connected_address.index(address)
    packet = create_packet(conn, index, flags)

    #conn.start()
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
    #conn.stop()
    clients.append(conn)

def send(conn: Conn, data: bytes) -> int:
    sends(conn, data)


def close(conn: Conn):
    conn.socket.close()
    logger.info(f'close connection')
    conn.socket = None


addres = "127.68.0.10:5000"
conn = listen(addres)
server_thread = threading.Thread(target=accept, args=(conn,))
server_thread.start()
clients = []
client_thread = threading.Thread(target=dial, args=(addres, clients))
client_thread.start()

server_thread.join()
client_thread.join()

print(conn.connected_address[0])
print(int.from_bytes(conn.ack[0], byteorder='big', signed=False))
print(int.from_bytes(conn.seq[0], byteorder='big', signed=False))

print(clients[0].connected_address[0])
print(int.from_bytes(clients[0].ack[0], byteorder='big', signed=False))
print(int.from_bytes(clients[0].seq[0], byteorder='big', signed=False))