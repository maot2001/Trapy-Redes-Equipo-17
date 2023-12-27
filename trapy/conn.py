import logging
import socket
import time
from utils import get_bytes, make_ip_header,make_protocol_header,unpack
from flags import Flags
from tcp import TCP_Header
from collections import deque
from testing_utils import get_testing_package_path
from converters_utils import parse_address,bytes_to_int

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
            self.is_server:bool=is_server
            self.tcp_header:TCP_Header=tcp_header
            self.windows_length = 4

            self.time_init: float = None
            self.time_out: float = 3000  # TODO:Definir el tiempo de parada
            self.time_mark: float = None
            self.time_estimated: float = 1
            self.time_desviation: float = 0
            self.time_interval: float = 1




            self.unacknowledge=deque()
              
            self.connected_bounds:list=[]
            if sock == None:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            self.socket = sock

    def start(self):
        now = time.time()
        self.time_mark = now
        if self.time_init == self.time_out:
            self.time_init = now

    def running(self):
        return self.time_init != self.time_out  # TODO: ????

    def time_out(self):
        if time.time() - self.time_init >= self.time_interval:
            self.time_interval *= 3 / 2
            self.time_init = self.time_out
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
        self.time_init = self.time_out

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
        temp=0
        if self.tcp_header.flags.ACK:temp=1
        if seq_num == -1: seq = 1
        if ack_num == -1: ack =temp
        protocol_header = make_protocol_header(s_port, d_port, seq_num if seq_num != -1 else self.seq,
                                               ack_num if ack_num != -1 else self.ack,
                                               self.windows_length, flags.ACK, flags.SYN, flags.FIN, data)
        return ip_header + protocol_header

   

    def copy_my_TCP_Head(self)->TCP_Header:
           
        t=self.tcp_header
        return TCP_Header(source_address=t.source_address,
                          destination_address=t.destination_address,
                          port_destination=t.port_destination,
                          port_source=t.port_source,
                            seq_number=t.seq_number,
                            ack_number=t.ack_number,
                            flags=t.flags,
                            recv_window=t.recv_window
                            
                                                     )
    
    
    def pack(self,flags:Flags,data:bytes,seq_num:int=-1)->bytes:
        
       header= self.tcp_header.create_tcp_header_to_bytes(seq_num,flags)
       
       return header+data
        
    def send_to_connect(self,step_number:int)->int:
         #flags con los que se armará la cabecera
         flags=Flags()
         if step_number == 1 and not self.is_server:
            flags.make_connection()
         elif step_number == 2 and not self.is_server:
             flags.hand_shake_ACK()
         elif step_number == 3 and not self.is_server:
            flags.recive_ACK()
         else:
            return 0
            #Preparar el paquete
         package=self.pack(flags=flags,data=b'')
         #ip:port
         dest=self.tcp_header.get_address_destination_to_str()
         dest_port=TCP_Header.get_property_from_bytes_to_int(self.tcp_header.port_destination)
         #enviar 
         self.socket.sendto(package,(dest,dest_port))
         #añadir a la pila el tiempo espera por el ACK msg
         
         self.unacknowledge.appendleft(time.time())
         
        
        
    #Acept
    def data_conn_Acept(self):
          #Si no llevo un paso implica que no se ha establecido la conexion correctamente
        while self.recive_conn(1)!=1:
             logging.info("Error while recieving SYN segment, retrying")
      
      
       #DEBUG: revisar que este correcto el listen
         
        str_addr=self.tcp_header.get_address_source_to_str()
        print(str_addr)
        str_dest_addr=self.tcp_header.get_address_destination_to_str()
        print(str_dest_addr)
        int_port_source=TCP_Header.get_property_from_bytes_to_int(self.tcp_header.port_source)
        print(int_port_source)
        #int_port_destino=TCP_Header.get_property_from_bytes_to_int(self.tcp_header.port_destination)
        #print(int_port_destino) 
        conn=Conn(tcp_header= self.copy_my_TCP_Head(),is_server=True)
        
        #Revisar el primer lugar donde este vacio y guardarlo ahi
        #en caso de no haber ninguno vacio lanzar advertencia de que
        # se lleno el maximo numero de conexiones
        for i in range(len(self.connected_bounds)):
                stored_conn = self.connected_bounds[i]
                if stored_conn == None or stored_conn.socket == None:
                    self.connected_bounds[i] = conn
                    break
        else:
             logging.warning("Maximum number of concurrent connections already reached.")
             time.sleep(2)
             return None
        local_timeout = time.time() + 15 + conn.time_out
            
        while time.time() < local_timeout:
            conn.send_to_connect(2)
            conn.socket.settimeout(conn.time_out)
            
            try:
                conn.tcp_header.refesh_seq()
                if conn.recive_conn(3) == 3:
                    break
                conn.tcp_header.add_seq(-1)
                logging.info("Error while recieving ACK segment, retrying.")
            except socket.timeout:
                conn.tcp_header.add_seq(-1)
                conn.time_out *= 2
                logging.info("Timeout while waiting for ACK segment, retrying")
        else:
            logging.error("Timeout ocurred while waiting for ACK, aborting")
            conn.socket.settimeout(None)
            return None
       
        conn.socket.settimeout(None)
        logging.info("Three-Way Handshake Completed")
        return conn
         
        
    
    
    
    def connect(self,address:bytes,port:bytes):
        self.is_server = False
        self.dest_hostport = parse_address(address)
        total_timeouts = 1
        local_timeout = time.time() + 15 + self.timeout
        while time.time() < local_timeout:
            self.send_connect(1)
            self.socket.settimeout(self.timeout)
            try:
                self.secnum += 1
                if self.recv_connect(2) == 2:
                    break
                self.secnum -= 1
                info("Error while recieving SYNACK segment, retrying")
            except socket.timeout:
                self.secnum -= 1
                total_timeouts *= 2 if total_timeouts < 32 else 1 
                self.timeout*=2
                info("Timeout ocurred while waiting for ACK segment, retrying.")
        else:
            self.socket.settimeout(None)
            return 0
        for _ in range(total_timeouts):
            self.send_connect(3)
        self.secnum += 1

        info("Three-Way Handshake completed, hopefully.")
        self.socket.settimeout(None)
        return 1
    
    
    
    
    def check_step(self,dest_ip:bytes,dest_port:bytes,step:int):
           source_host=self.tcp_header.get_address_source_to_str()
           
           source_port=TCP_Header.get_property_from_bytes_to_int(self.tcp_header.port_source)
           
           if TCP_Header.get_address_from_bytes_to_str(dest_ip) != source_host:
               
            if (not self.is_server) and step == 2 and (source_host==""and source_port==0):
                
                self.tcp_header.set_source_address(dest_ip)
                self.tcp_header.set_source_port(dest_port)
                
            else:
                logging.error(f"Wrong Address, information was meant to {dest_ip} instead of this({source_host}):({source_port})).")
                return False
            return True

    def recive_conn(self,step_number:int)->int:
       try:
            #Se recibe un paquete de 1024 bytes
            #TODO:Quitar depsues de debuggear packet, _ = self.socket.recvfrom(1024)
            packet= get_testing_package_path()
       except:
            logging.exception('Error al recibir el paquete')
            
            return 0

       
        #Devuelve TCP_Header y los datos, hace las comprobaciones del checksum 
       try :
            
        tcp_Header, data = unpack(packet)
        source_addr=tcp_Header.source_address
        source_port=tcp_Header.port_source
        
        destination_addr=tcp_Header.destination_address
        destination_port=tcp_Header.port_destination
        
        
       except:
            logging.exception('Error al desempaquetar el paquete')
            return 0
            
       if(not self.check_step(destination_addr,destination_port,step_number)):
            logging.info("Error al verificar el paso")
       
       
       #TODO:Revisar esto
       if source_addr != self.tcp_header.destination_address:
            if self.is_server and step_number == 1:
                self.tcp_header.destination_address = source_addr
                self.tcp_header.connect_port = source_port
                
            elif self.client and step_number== 2 and source_addr == self.tcp_header.destination_address:
                 self.tcp_header.destination_address = source_addr
                 self.tcp_header.connect_port = source_port
            else:
                logging.info(f"Wrong Address, information arrived from {source_addr}:{source_port} instead of {self.tcp_header.destination_address}.")
                return self.recv_connect(step_number)
            
       ## elementos dinamicos de las ventans  self.dynamic_segment_size = min(recv_window, self.dynamic_segment_size)
       flags=tcp_Header.flags
       
       if step_number == 1 and self.is_server and flags.SYN:
            self.acknum =tcp_Header.refesh_seq()
            return step_number
        
       if ((step_number == 2 and self.is_server  and flags.SYN and flags.ACK) or (step_number == 3 and self.is_server and flags.ACK)) and self.tcp_header.seq_number == tcp_Header.ack_number:
           
            self.tcp_header.set_ack_num(tcp_Header.seq_number)
            self.tcp_header.refesh_ack() 
            send_time = self.unacknowledge.pop()
            #TODO:Implementar aumentar la ventana de tiempo
            #self.update_timeout(send_time)
            return step_number
       return 0
   
   
   
   
   
   
   
   
   
   
   
   
   
class ConnException(Exception):
        pass
    # TODO: Implementar excepciones
