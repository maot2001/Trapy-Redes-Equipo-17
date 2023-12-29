import logging
import time
import random
import threading
from utils import *
from conn import *
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
        time_out = 0#veces que modifico el timeout
        timer = time.time()  # Inicializa timer para la primera transmisión
        conn.socket.sendto(packet, conn.connected_address[index])
        conn.socket.settimeout(0.5)

        while True:
            try:
                packet, _ = conn.socket.recvfrom(1024)
                address, protocol, _, flags = data_conn(packet)
            except:
                if time.time() - timer >= conn.time_out:  # Retransmitir si timeout
                    time_out = time_out+1
                    if(time_out>5):#actualiza el timeout pq tal vez es muy pequeño
                        conn.time_out = conn.time_out +2
                    conn.socket.sendto(packet, conn.connected_address[0])
                    timer = time.time()  # Reiniciar timer
                    if(conn.time_out>60):# revisa q no este esperando mas de un minuto
                        raise ConnException()
                continue

            ack = int.from_bytes(conn.seq[index], byteorder='big', signed=False)
            ack += 1
            if protocol[4:8] != conn.ack[index] or protocol[8:12] != ack.to_bytes(4,byteorder='big', signed=False) or flags.ACK == 0:
                continue

            logger.info(f'ack received')
            conn.refresh(index, int.from_bytes(protocol[8:12], byteorder='big', signed=False), int.from_bytes(protocol[4:8], byteorder='big', signed=False), 0)
            timer = time.time()# como el ack esperado es correcto reinicia el tiempo
            time_out = 0
            conn.time_out = 2
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
    time_out = 0#veces que modifico el timeout
    timer = time.time()  # Inicializa timer para la primera transmisión
    conn.socket.sendto(packet, conn.connected_address[index])
    conn.socket.settimeout(0.5)

    while True:
        try:
            packet, _ = conn.socket.recvfrom(1024)
            address, protocol, _, flags = data_conn(packet)
        except:
            if time.time() - timer >= conn.time_out:  # Retransmitir si timeout
                time_out = time_out+1
                if(time_out>5):#actualiza el timeout pq tal vez es muy pequeño
                    conn.time_out = conn.time_out +2
                conn.socket.sendto(packet, conn.connected_address[0])
                timer = time.time()  # Reiniciar timer
                if(conn.time_out>60):# revisa q no este esperando mas de un minuto
                    raise ConnException()
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

        timer = time.time()# como el ack esperado es correcto reinicia el tiempo
        time_out = 0
        conn.time_out = 2
        break
    return conn

def send(conn: Conn, data: bytes) -> int:
    send_close(conn, 0, True)
    return 0
    mss: int = 1024
    data_len = len(data)
    flags = Flags()
    packet = create_packet(conn, 0, flags, data)
    time_out = 0#veces que modifico el timeout

    timer = time.time()  # Inicializa timer para la primera transmisión
    conn.socket.sendto(packet, conn.connected_address[0])
    conn.socket.settimeout(0.5)

    while True:
        try:
            packet, _ = conn.socket.recvfrom(mss)
            address, protocol, data, flags = data_conn(packet)
        except:
            if time.time() - timer >= conn.time_out:  # Retransmitir si timeout
                time_out = time_out+1
                if(time_out>5):#actualiza el timeout pq tal vez es muy pequeño
                    conn.time_out = conn.time_out +2
                conn.socket.sendto(packet, conn.connected_address[0])
                timer = time.time()  # Reiniciar timer
                if(conn.time_out>60):# revisa q no este esperando mas de un minuto
                    raise ConnException()
            continue

        if address != conn.connected_address[0]:
            continue
        
        tcp_header = Protocol_Wrapped(protocol)
        seq = convert_bytes_to_int(conn.seq[0])
        seq += data_len
        rec_ack = convert_bytes_to_int(tcp_header.ack_num)
        
        if flags.ACK == 0 or seq != rec_ack:
            continue

        timer = time.time()# como el ack esperado es correcto reinicia el tiempo
        time_out = 0
        conn.time_out = 2
        break
    return data_len

def recv(conn: Conn, length: int) -> bytes:
    data = 0
    count = 0
    conn.socket.settimeout(0.5)
    while True:
        try:
            packet, _ = conn.socket.recvfrom(length)
            address, protocol, data, flags = data_conn(packet)
        except:
            print(count)
            if count > 20:
                break
            count +=1
            continue
        
        if not address in conn.connected_address:
            continue

        index = conn.connected_address.index(address)
        if flags.SYN == 1 or flags.ACK == 1:
            continue

        if flags.FIN == 1 or flags.RST == 1:
            close_thread = threading.Thread(target=close, args=(conn, index, flags.FIN == 1))
            close_thread.start()
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

def send_close(conn: Conn, index: int, fin: bool):
    if (fin):
        flags = Flags()
        flags.FIN = 1
        packet = create_packet(conn, index, flags)
        logger.info(f'fin sending')

        time_out = 0#veces que modifico el timeout
        timer = time.time()  # Inicializa timer para la primera transmisión
        conn.socket.sendto(packet, conn.connected_address[0])
        conn.socket.settimeout(0.5)

        while True:
            try:
                packet, _ = conn.socket.recvfrom(1024)
                address, protocol, _, flags = data_conn(packet)
            except:
                if time.time() - timer >= conn.time_out:  # Retransmitir si timeout
                    time_out = time_out+1
                    if(time_out>5):#actualiza el timeout pq tal vez es muy pequeño
                        conn.time_out = conn.time_out +2
                    conn.socket.sendto(packet, conn.connected_address[0])
                    timer = time.time()  # Reiniciar timer
                    if(conn.time_out>60):# revisa q no este esperando mas de un minuto
                        raise ConnException()
                continue
            
            if address != conn.connected_address[index]:
                continue

            ack = int.from_bytes(conn.seq[index], byteorder='big', signed=False) + 1
            if flags.ACK == 0 or flags.FIN == 0 or protocol[8:12] != ack.to_bytes(4,byteorder='big', signed=False):
                continue

            logger.info(f'fin-ack received')
            conn.refresh(index, int.from_bytes(protocol[8:12], byteorder='big', signed=False), int.from_bytes(protocol[4:8], byteorder='big', signed=False), 1)

            flags = Flags()
            flags.ACK = 1
            packet = create_packet(conn, index, flags)
            logger.info(f'ack sending')
            conn.socket.sendto(packet, conn.connected_address[index])

            timer = time.time()# como el ack esperado es correcto reinicia el tiempo
            time_out = 0
            conn.time_out = 2
            break
    
    else:
        flags = Flags()
        flags.RST = 1
        packet = create_packet(conn, index, flags)
        logger.info(f'rst sending')
        conn.socket.sendto(packet, conn.connected_address[index])
    
    logger.info(f'close connection')
    conn.connected_address.pop(index)
    conn.ack.pop(index)
    conn.seq.pop(index)

def close(conn: Conn, index: int, fin: bool):
    if (fin):
        ack = convert_bytes_to_int(conn.ack[index]) + 1
        conn.ack[index] = ack.to_bytes(4, byteorder='big', signed=False)
        flags = Flags()
        flags.FIN = 1
        flags.ACK = 1
        packet = create_packet(conn, index, flags)
        logger.info(f'fin-ack sending')

        time_out = 0#veces que modifico el timeout
        timer = time.time()  # Inicializa timer para la primera transmisión
        conn.socket.sendto(packet, conn.connected_address[index])
        conn.socket.settimeout(0.5)

        while True:
            try:
                packet, _ = conn.socket.recvfrom(1024)
                address, protocol, _, flags = data_conn(packet)
            except:
                if time.time() - timer >= conn.time_out:  # Retransmitir si timeout
                    time_out = time_out+1
                    if(time_out>5):#actualiza el timeout pq tal vez es muy pequeño
                        conn.time_out = conn.time_out +2
                    conn.socket.sendto(packet, conn.connected_address[0])
                    timer = time.time()  # Reiniciar timer
                    if(conn.time_out>60):# revisa q no este esperando mas de un minuto
                        raise ConnException()
                continue

            ack = int.from_bytes(conn.seq[index], byteorder='big', signed=False)
            ack += 1
            if protocol[4:8] != conn.ack[index] or protocol[8:12] != ack.to_bytes(4,byteorder='big', signed=False) or flags.ACK == 0:
                continue

            logger.info(f'ack received')
            timer = time.time()# como el ack esperado es correcto reinicia el tiempo
            time_out = 0
            conn.time_out = 2
            break

    logger.info(f'close connection')
    conn.connected_address.pop(index)
    conn.ack.pop(index)
    conn.seq.pop(index)
    time.sleep(60)