import logging
import socket
import time
from utils import get_bytes, make_ip_header,make_protocol_header,unpack
from flags import Flags
from tcp import TCP_Header

# Configura el logger para que registre los mensajes en un archivo
logging.basicConfig(filename='app.log', level=logging.INFO)

class Conn:
    """
    Esta es la clase Conn. Aquí puedes describir la clase.

    Atributos
    ---------
    origin_address : type
       Address origen.
    connected_address : type
       Address Destino.
    ack : bytes
    
        Descripción de ack. 
    seq : bytes
        Descripción de # secuencia.
    windows_length : int
        Descripción de windows_length.-
        
    """

    def __init__(self,tcp_header:TCP_Header,is_server:bool, sock=None):
            """
            Initializes a connection object.

            Args:
                tcp_header (TCP_Header): The TCP header object.
                is_server (bool): Indicates whether the connection is for a server or client.
                sock (socket, optional): The socket object. Defaults to None.
            """
            self.is_server:bool=
            self.tcp_header:TCP_Header=tcp_header
            self.windows_length = 4

            self.time_init: float = None
            self.time_stop: float = None  # TODO:Definir el tiempo de parada
            self.time_mark: float = None
            self.time_estimated: float = 1
            self.time_desviation: float = 0
            self.time_interval: float = 1

            self.connected_bounds:list=[]
            if sock == None:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            self.socket = sock

    def start(self):
        now = time.time()
        self.time_mark = now
        if self.time_init == self.time_stop:
            self.time_init = now

    def running(self):
        return self.time_init != self.time_stop  # TODO: ????

    def timeout(self):
        if time.time() - self.time_init >= self.time_interval:
            self.time_interval *= 3 / 2
            self.time_init = self.time_stop
            # Aumentar la ventana de tiempo
            return True
        return False

    def waiter(self, time_wait):
        return self.running() and time.time() - self.time_mark >= time_wait

    def stop(self, retime=True):
        if retime:
            elapsed = time.time() - self.time_init
            self.time_estimated *= 7 / 8
            self.time_estimated += elapsed / 8

            self.time_desviation *= 3 / 4
            self.time_desviation += abs(elapsed - self.time_estimated) / 4

            self.time_interval = self.time_estimated + 4 * self.time_desviation
        self.time_init = self.time_stop

    def refresh(self, protocol):
        self.seq = get_bytes(protocol, 8, 12)
        self.ack = get_bytes(protocol, 4, 8) + 1

    def create_package(self, flags: Flags, seq_num=-1, ack_num=-1, data=b''):
        s_address, s_port = self.origin_address
        d_address, d_port = self.connected_address
        if d_address == 'localhost':
            d_address, d_port = self.socket.getsockname()
        ip_header = make_ip_header(s_address, d_address)
        # TODO: Hay que hacer esto desde que se crea el objeto COnn
        # if seq == -1: seq = conn.seq
        
        if seq == -1: seq = 1
        if ack == -1: ack = conn.ack
        protocol_header = make_protocol_header(s_port, d_port, seq_num if seq_num != -1 else self.seq,
                                               ack_num if ack_num != -1 else self.ack,
                                               self.windows_length, flags.ACK, flags.SYN, flags.FIN, data)
        return ip_header + protocol_header

   
    """
    def data_conn(self):
        try:
            #Se recibe un paquete de 1024 bytes
            packet, _ = self.socket.recvfrom(1024)
        except:
            logging.info('Error al recibir el paquete')
            return None

        #TODO:Revisar el checkSum
        
        ip_header, protocol, data = packet[20:40], packet[40:60], packet[60:]
        if corrupt(protocol , data):
            return None
        
        #ip = '.'.join(map(str, ip_header[12:16]))
        ip_source=get_address_from_bytes(ip_header[12:16])
        ip_dest=get_address_from_bytes(ip_header[16:20])
        
        port = int.from_bytes(protocol[:2], byteorder='big', signed=False)

        return ((ip_source, port), protocol, data)
        
   """
    def data_conn(self):
        try:
            #Se recibe un paquete de 1024 bytes
            packet, _ = self.socket.recvfrom(1024)
        except:
            logging.info('Error al recibir el paquete')
            return None

       
        #Devuelve TCP_Header y los datos, hace las comprobaciones del checksum 
        TCP_Header, data = unpack(packet)
        
        
        
        
       

   
   
    
   
    class ConnException(Exception):
        pass
    # TODO: Implementar excepciones
