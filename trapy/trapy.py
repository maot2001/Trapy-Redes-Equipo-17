import logging
import time
from utils import *
from conn import *
import flags
logger = logging.getLogger(__name__)



def listen(address: str):
    conn = Conn()
    conn.origin_address = parse_address(address)
    print(conn.origin_address)
    conn.socket.bind(('127.0.0.1',8000))
   
    logger.info(f'socket binded to {address}')

   # conn.socket.listen(10)

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

        logger.info(f'syn received')
        conn.stop()

        accept_conn = Conn()

        accept_conn.origin_address = conn.origin_address
        accept_conn.connected_address = address

        accept_conn.ack = get_bytes(protocol, 4, 8) + 1

        packet = create_packet(accept_conn, ACK = 1, SYN = 1)

        conn.start()

        logger.info(f'syn-ack sending')
        accept_conn.socket.sendto(packet, accept_conn.connected_address)

        while True:
            if not accept_conn.running() or accept_conn.timeout():
                logger.warning(f'syn-ack sending again')
                accept_conn.socket.sendto(packet, accept_conn.connected_address)
                accept_conn.origin_address = conn.origin_address

            if accept_conn.waiter(180):
                accept_conn.stop()
                logger.error(f'error sending')
                raise ConnException()

            try:
                address, protocol, _ = data_conn(accept_conn)
            except:
                continue

            if get_bytes(protocol, 4, 8) != accept_conn.ack or get_bytes(protocol, 8, 12) != accept_conn.seq + 1 or \
            not protocol[17] == 1:
                continue

            logger.info(f'ack received')
            accept_conn.refresh(protocol)
            accept_conn.stop()
            return accept_conn


def dial(address: str):
    conn = Conn()
    conn.origin_address = conn.socket.getsockname()
    conn.connected_address = parse_address(address)
    conn.ack = 1

    packet = create_packet(conn, SYN = 1)

    conn.start()
    logger.info(f'syn sending')
    conn.socket.sendto(packet, conn.connected_address)

    while True:
        if not conn.running() or conn.timeout():
            logger.warning(f'syn sending again')
            conn.socket.sendto(packet, conn.connected_address)
            conn.origin_address = conn.socket.getsockname()
            conn.time_init = time.time()
            
        if conn.waiter(180):
            conn.stop()
            logger.error(f'error sending')
            #TODO: Poner la exepcionraise ConnException()
        
        try:
            address, protocol, _ = data_conn(conn)
        except:
            continue
        
        if protocol[17] == 1 and protocol[14] == 1 and get_bytes(protocol, 8, 12) == conn.seq + 1:
            logger.info(f'syn-ack received')
            conn.refresh(protocol)
            conn.connected_address = address
            conn.origin_address = conn.socket.getsockname()

            logger.info(f'ack sending')
            packet = create_packet(conn, ACK = 1)
            conn.socket.sendto(packet, conn.connected_address)
            break
    conn.stop()
    return conn


def send(conn: Conn, data: bytes) -> int:
    
    #Secuencia 
    sequence=conn.seq
    ack=conn.ack
    times = 0
    #Tramas
    frames= pieces = [data[i:min(len(data),i + 1024)]for i in range(0,len(data),1024)]
    
    current={sequence:0}
    
    for i in range(current[conn.sequence_number], min(current[conn.sequence_number] + conn.windows_size, len(pieces))):
         current[seq_num] = i
       # Crear el paquete
         package = conn.package(seq_num=seq_num,ack_num=conn.ack+i-current[conn.sequence_number],data=pieces[i])
          
                   #Enviamos el paquete
                   #TODO:Verificar si se envia a la direccion correcta osea es una tupla ('direcciopon',puerto:int)
         conn.socket.sendto(package, (conn.destination_address,0))
         seq_num +=len(pieces[i])
         conn.timer.start()
         current[seq_num] = min(current[conn.sequence_number]+conn.windows_size, len(pieces))

def recv(conn: Conn, length: int) -> bytes:
    buffer = b''
    count = 0

    conn.start()

    while len(buffer) <length:
        try:
            _, protocol, data = data_conn(conn)
        except:
            if not conn.running() or conn.timeout():
                count += 1

                packet = create_packet(conn, ACK = 1)
                conn.socket.sendto(packet, conn.connected_address)

            if conn.waiter(30):
                conn.stop()
                logger.error(f'error receiving')
                raise ConnException()
            continue

        if get_bytes(protocol, 4, 8) != conn.ack or get_bytes(protocol, 8, 12) != conn.seq + 1:
            continue

        if protocol[13] == 1:
            conn.stop()
            conn.refresh(protocol)
            
            packet = create_packet(conn, ACK = 1, FIN = 1)
            conn.time_mark = time.time()
            conn.socket.sendto(packet, conn.connected_address)
            
            conn.stop()
            return buffer
        else:
            conn.time_mark = time.time()
            conn.stop(count <= 2)

            if len(buffer) + len(data) >= length:
                data = data[:length - len(buffer)]

            buffer += data
            conn.seq = get_bytes(protocol, 8, 12)
            conn.ack += len(data)
            count = 0
    
    conn.stop()

    if len(buffer) == length:
        packet = create_packet(conn, ACK = 1, FIN = 1)
        end(conn, packet)
    
    return buffer


def close(conn: Conn):
    conn.socket.close()
    logger.info(f'close connection')
    conn.socket = None




dial("127.0.0.1:8000")
