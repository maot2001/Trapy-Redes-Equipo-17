import logging
import random
from utils import *
from conn import *
#from trapy.timer import Timer




import time


class Timer(object):
    TIMER_STOP = -1

    def __init__(self, duration):
        self._start_time = self.TIMER_STOP
        self._duration = duration

    # Starts the timer
    def start(self):
        if self._start_time == self.TIMER_STOP:
            self._start_time = time.time()

    # Stops the timer
    def stop(self):
        if self._start_time != self.TIMER_STOP:
            self._start_time = self.TIMER_STOP

    # Determines whether the timer is running
    def running(self):
        return self._start_time != self.TIMER_STOP

    # Determines whether the timer timed out
    def timeout(self):
        if not self.running():
            return False
        else:
            return time.time() - self._start_time >= self._duration

    # Current time since timer started in seconds
    def time(self):
        return time.time() - self._start_time






#Esto ahora mismo no esta haciendo nada relevante, no le presten mucha atencion, es un print bonito
logger = logging.getLogger(__name__)

def listen(address: str):
    #Aqui no se hace nada especial, solo crear un conn y hacerle bind a su socket
    conn = Conn()

    conn.origin_address = parse_address(address)

    conn.socket.bind(conn.origin_address)
    logger.info(f'socket binded to {address}')

    return conn

def accept(conn: Conn):

    while True:
        try:
            """
            Esta es la lectura estandar, que se apoya en data_conn para separar el packet, aqui se espera un paquete de inicio
            de conexion (1er mensaje)
            address = direccion desde la que se envia el paquete
            protocol = la cabecera del protocolo tcp usada
            flags = un objeto Flags con todas las flags activas en el paquete
            """
            packet, _ = conn.socket.recvfrom(1024)
            address, protocol, _, flags = data_conn(packet)
            #Aqui se pueden lanzar errores por el checksum
        except:
            continue

        #Si no es un paquete de inicio de conexion se ignora
        if flags.SYN == 0:
            continue
        
        #Si ya existe una conexion entre ellos se ignora
        if address in conn.connected_address:
            logger.error(f'existing connection with {address}')
            continue

        logger.info(f'syn received from {address}')

        conn.connected_address.append(address)
        
        """
        En protocol[4:8] esta el seq del client, este se aumenta a 1 y se toma como ack del server
        Esta implementado asi xq sumar los bytes me dio muchos errores y al final lo cambie a int, para luego regresarlo a byte,
        si encuentran una forma comoda de hacer esto en bytes avisen, sino creo q seria mejor cambiar conn.ack y conn.seq a 
        list(int) para suavizar el codigo xq estos cambios son lo q mas feo se ve
        """
        seq = int.from_bytes(protocol[4:8], byteorder='big', signed=False)
        seq += 1
        conn.ack.append(seq.to_bytes(4,byteorder='big', signed=False))

        #Aqui se crea el seq del server
        tmp = random.randint(2, 1e6)
        conn.seq.append(tmp.to_bytes(4,byteorder='big',signed=False))
        
        #El objeto flags por default tiene todas las banderas en 0
        flags = Flags()
        flags.ACK = 1
        flags.SYN = 1

        """
        Para crear el paquete hay q enviarle la conn, el index (para que pueda saber los datos de las 3 listas) y las flags
        activas (me parecio que abstraer de esto los metodos del trapy les seria comodo para trabajar en recv y send)
        """
        index = conn.connected_address.index(address)
        packet = create_packet(conn, index, flags)

        #Se envia el paquete creado (2do mensaje)
        logger.info(f'syn-ack sending')
        conn.socket.sendto(packet, conn.connected_address[index])

        while True:
            #Timers se implementaran luego
            """if not accept_conn.running() or accept_conn.timeout():
                logger.warning(f'syn-ack sending again')
                accept_conn.socket.sendto(packet, accept_conn.connected_address)
                accept_conn.origin_address = conn.origin_address

            if accept_conn.waiter(180):
                accept_conn.stop()
                logger.error(f'error sending')
                raise ConnException()"""

            try:
                #Se espera el 3er mensaje del tree handshake
                packet, _ = conn.socket.recvfrom(1024)
                address, protocol, _, flags = data_conn(packet)
            except:
                continue

            #Se verifica que ese mensaje tiene el ack y seq correctos, ademas de la flag de ACK, en caso contrario se ignora
            ack = int.from_bytes(conn.seq[index], byteorder='big', signed=False)
            ack += 1
            if protocol[4:8] != conn.ack[index] or protocol[8:12] != ack.to_bytes(4,byteorder='big', signed=False) or flags.ACK == 0:
                continue

            logger.info(f'ack received')
            #Ya se establecio la conexion, tree handshake completado, luego se actualizan los valores de ack y seq en el server
            conn.refresh(index, int.from_bytes(protocol[8:12], byteorder='big', signed=False), int.from_bytes(protocol[4:8], byteorder='big', signed=False), 0)
            return conn

def dial(address: str, clients) -> Conn:
    address = parse_address(address)
    conn = Conn()
    #Aqui se solicita un ip y un puerto vacio para asignar al client
    conn.socket.bind(('0.0.0.0', 0)) 
    conn.origin_address = conn.socket.getsockname()

    conn.connected_address.append(address)

    #Se asigna el ack y seq para el 1er envio 
    conn.ack.append(int(0).to_bytes(4,byteorder='big',signed=False))
    tmp = random.randint(2, 1e6)
    conn.seq.append(tmp.to_bytes(4,byteorder='big',signed=False))

    #Se activa la flag de inicio de conexion
    flags = Flags()
    flags.SYN = 1

    #Nuevamente creacion del paquete con los valores necesarios, explicacion analoga al accept del server
    index = conn.connected_address.index(address)
    packet = create_packet(conn, index, flags)

    #Se envia el 1er mensaje
    logger.info(f'syn sending')
    conn.socket.sendto(packet, conn.connected_address[index])

    while True:
        #Timers se implementaran luego
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
            #Se espera el mensaje de respuesta del servidor a la solicitud de conexion (2do mensaje)
        except:
            continue
        
        #Se verifica que el valor de ack sea el correcto, asi como las flags de ack y syn, en caso contrario se ignora
        ack = int.from_bytes(conn.seq[index], byteorder='big', signed=False)
        ack += 1
        if flags.ACK == 0 or flags.SYN == 0 or protocol[8:12] != ack.to_bytes(4,byteorder='big', signed=False):
            continue

        logger.info(f'syn-ack received')
        #Se actualizan los valores de ack y seq
        conn.refresh(index, int.from_bytes(protocol[8:12], byteorder='big', signed=False), int.from_bytes(protocol[4:8], byteorder='big', signed=False), 1)

        #Activar flag para ultimo mensaje
        flags = Flags()
        flags.ACK = 1
        
        packet = create_packet(conn, index, flags)
        
        logger.info(f'ack sending')
        conn.socket.sendto(packet, conn.connected_address[index])
        #Se envia y se termina el tree handshake (debo poner las rectificaciones de si no llegan y cosas x el estilo)
        break
    clients.append(conn)
    #esto es para sacar la conexion del cliente del hilo

def send(conn: Conn, data: bytes) -> int:
    if conn.is_close:
        return 0
    data_send = 0
    sender_timer = Timer(conn.duration)
    sender_timer.start()
    packets_data = divide_data(data, conn.max_data_packet)
    conn.send_base = 0

    timers = [Timer(1) for _ in range(len(packets_data))]
    is_packet_send = [False for i in range(len(packets_data))]

    print(f"LEN DATA: {len(packets_data)}")
    windows_recv_packets = 0
    window_timeout = False
    while conn.send_base < len(packets_data) and not sender_timer.timeout():
        window = range(conn.send_base, min(conn.send_base + conn.N, len(packets_data)))

        logger.info(f"WINDOW SIZE: {conn.N}")
        print(f"WINDOW SIZE : {conn.N}")

        for i, packet_index in enumerate(window):
            if not is_packet_send[packet_index] or timers[packet_index].timeout():
                flags = 0
                if packet_index == len(packets_data) - 1:
                    flags = LAST_FLAG
                p = Packet(src_port=conn.get_port(),
                           dest_port=conn.get_dest_address()[1],
                           seq_number=(conn.send_base_sequence_number + i) & 0xffffffff,
                           data_len=len(packets_data[packet_index]),
                           data=packets_data[packet_index],
                           flags=flags)
                is_packet_send[packet_index] = True
                print(f'SeqNum send:{p.seq_number}')
                logger.info(f'SeqNum send:{p.seq_number}')
                conn.send(p.build())

                if timers[packet_index].timeout():
                    window_timeout = True

                timers[packet_index] = Timer(0.5)
                timers[packet_index].start()

        recv_packet, _ = conn.recv()

from recive_utils import join_byte_arrays
def recv(conn: Conn, length: int) -> bytes:
    
    
    
    mss:int=1024
    
    
    
    #TODO: Añadir que el tamaño de ventana tiene que ser <= length restante    
    #TODO:Añadir en caso que el window lengh es > length hay que corregirlo
 
    buffer:list=[]
    buffer_length:int=0
    
    while True:
       # packet=b'E\x00\x00<E\xb2@\x00@\x06\xf7\x06\x7f\x00\x00\x01\x7f\x00\x00\x02E\x00\x00(\x00\x01\x00\x00@\x06|\xcc\x7f\x00\x00\x01\x7f\x00\x00\x02\x04\xd6\x1f@\x00\x00\x00\x00\x00\x00\x00\x00P\x02 \x00m\xc9\x00\x00'
       #
       # packet=b'E\x00\x00FZ\xa6@\x00@\x06\xe2\x08\x7f\x00\x00\x01\x7f\x00\x00\x02E\x00\x002\x00\x01\x00\x00@\x06|\xc2\x7f\x00\x00\x01\x7f\x00\x00\x02\x04\xd6\x1f@\x00\x00\x00\x00\x00\x00\x00\x00P\x02 \x00]\x9b\x00\x00holamuindo'
        packet, _ = conn.socket.recvfrom(mss)
        print("jn")
        address, protocol, data, flags = data_conn(packet)
        """
        try:
            packet, _ = conn.socket.recvfrom(mss)
            address, protocol, data, flags = data_conn(packet)
           
        except:
            continue
        """
        #Si es acuse de recibo continuar
        """
        Momentáneamente si el ACK=1 => que es un mensaje de confirmación de algún tipo
        """
        print("hola")
        if(flags.ACK):
            continue
        print(len(data))
        new_date_l=len(data)
        
        
        if(buffer_length+new_date_l>length):
           return join_byte_arrays(buffer) 
        
        buffer.append(data)
        buffer_length+=new_date_l
        
        if(buffer_length+new_date_l==length):
            return join_byte_arrays(buffer) 
            
        if flags.ACK == 0:
            continue

        index = conn.connected_address.index(address)
        ack = int.from_bytes(conn.seq[index], byteorder='big', signed=False)
        ack += 1
        if protocol[8:12] != ack.to_bytes(4,byteorder='big', signed=False):
            continue

        logger.info(f'ack received')
        conn.refresh(index, int.from_bytes(protocol[8:12], byteorder='big', signed=False), int.from_bytes(protocol[4:8], byteorder='big', signed=False), 0)

        return join_byte_arrays(buffer)
    

def close(conn: Conn):
    conn.socket.close()
    logger.info(f'close connection')
    conn.socket = None

"""
addres = "127.68.0.10:5000"
conn = listen(addres)
server_thread = threading.Thread(target=accept, args=(conn,))
server_thread.start()
clients = []
client_thread = threading.Thread(target=dial, args=(addres, clients))
client_thread.start()

#server_thread.join()
#client_thread.join()

print(conn.connected_address[0])
print(int.from_bytes(conn.ack[0], byteorder='big', signed=False))
print(int.from_bytes(conn.seq[0], byteorder='big', signed=False))

print(clients[0].connected_address[0])
print(int.from_bytes(clients[0].ack[0], byteorder='big', signed=False))
print(int.from_bytes(clients[0].seq[0], byteorder='big', signed=False))
"""