import logging
import time
import random
import threading
from utils import *
from conn import *
import threading
import time
from packet import *
from timer import Timer
logger = logging.getLogger(__name__)

def listen(address: str):
    conn = Conn()

    conn.origin_address = parse_address(address)
    print(conn.origin_address)

    conn.socket.bind(conn.origin_address)
    logger.info(f'socket binded to {address}')

    return conn

def accept(conn: Conn):
    #conn.start()

    while True:
        try:
            packet, _ = conn.socket.recvfrom(1024)
            print(f'server reading syn packet')
            address, protocol, _, flags = data_conn(packet)
        except:
            print(f'server non-reading syn packet')
            continue

        if not flags.SYN:
            continue
        
        if address in conn.connected_address:
            logger.error(f'existing connection with {address}')
            continue

        print(f'server syn received from {address}')
        logger.info(f'syn received')
        #conn.stop()

        conn.connected_address.append(address)
        conn.ack.append(protocol[4:8] + 1)
        tmp = random.randint(2, 1e10)
        print(f'server seq: {tmp}')
        conn.seq.append(tmp.to_bytes(4,byteorder='big',signed=False))
        
        flags = Flags()
        flags.ACK = 1
        flags.SYN = 1

        index = conn.connected_address.index(address)
        packet = create_packet(conn, index, flags)

        #conn.start()

        print(f'server syn-ack sending to {address}')
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
                print(f'server reading ack packet')
                address, protocol, _, flags = data_conn(packet)
            except:
                print(f'server non-reading ack packet')
                continue

            if protocol[4:8] != conn.ack[index] or protocol[8:12] != conn.seq[index] + 1 or not flags.ACK:
                continue

            print(f'server ack received')
            logger.info(f'ack received')
            #conn.refresh(protocol)
            #accept_conn.stop()
            return conn

def dial(address: str) -> Conn:
    address = parse_address(address)
    conn = Conn()
    conn.origin_address = conn.socket.getsockname()
    conn.connected_address.append(address)

    tmp = 0
    conn.ack.append(tmp.to_bytes(4,byteorder='big',signed=False))
    tmp = random.randint(2, 1e10)
    print(f'client seq: {tmp}')
    conn.seq.append(tmp.to_bytes(4,byteorder='big',signed=False))

    flags = Flags()
    flags.SYN = 1

    index = conn.connected_address.index(address)
    packet = create_packet(conn, index, flags)

    #conn.start()
    print(f'client syn sending')
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
            print(f'client reading syn-ack packet')
            address, protocol, _, flags = data_conn(packet)
        except:
            print(f'client non-reading syn-ack packet')
            continue
        
        if not flags.ACK or not flags.SYN or protocol[8:12] != conn.seq[index] + 1:
            continue

        print(f'client syn-ack received')
        logger.info(f'syn-ack received')
        #conn.refresh(protocol)

        conn.refresh(index, protocol[8:12], protocol[4:8], 1)
        flags = Flags()
        flags.ACK = 1
        
        print(f'client ack sending')
        logger.info(f'ack sending')
        packet = create_packet(conn, index, flags)
        conn.socket.sendto(packet, conn.connected_address[index])
        break
    #conn.stop()
    return conn




def close(conn: Conn):
    conn.socket.close()
    logger.info(f'close connection')
    conn.socket = None


addres = "127.0.0.1:8000"
conn = listen(addres)
server_thread = threading.Thread(target=accept, args=(conn,))
server_thread.start()
client_thread = threading.Thread(target=dial, args=(addres,))
client_thread.start()

time.sleep(30)
print(conn.connected_address[0])
print(conn.ack[0])
print(conn.seq[0])