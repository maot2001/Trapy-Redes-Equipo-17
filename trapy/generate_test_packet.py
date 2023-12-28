from utils import *
from flags import *
import socket
from trapy import *

#crear el paquete 

def create_packet(o_addr:str,c_addr:str,o_port:int,c_port:int,seq:bytes,ack:bytes, flags: Flags,windows_length:int=40, data = b''):
   

    #Para la cabecera del ip, solo hacen falta los 2 ip correspondientes a origen y destino
    ip_header = build_iph(o_addr, c_addr)

    """
    Para la cabecera del tcp se necesita, los 2 puertos, el seq y ack del que va transmitir el paquete (a la conexion 
    correspondiente), el tamaño de ventana (con eso se va a trabajar mas en el send y el recv), las flags activas en un
    objeto de tipo Flags y los datos

    Dentro de build_protocolh se calcula el checksum correspondiente
    """
    protocol_header = build_protocolh(o_port, c_port, seq, ack, windows_length, flags, data)
    
    return ip_header + protocol_header


o_addr="127.0.0.1"
o_port=800
d_addr='0.0.0.0'
d_port=85
seq=int_to_bytes(50,4)
ack=int_to_bytes(30,4)

flags=Flags()

data=b'hola mundo'


packet=create_packet(o_addr=o_addr,
        c_addr=d_addr,
        o_port=o_port,
        c_port=d_port,
        seq=seq,
        ack=ack,
        flags=flags,
        data=data)
        
# Crear un socket
print(5)
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
s.sendto(packet, ("127.0.0.2", 8000))

conn=listen("127.0.0.1:50")
accept(conn)
conn2=dial("127.0.0.1:50")
print(conn.connected_address[0])
recv(conn,1000)
print("Listo") 
    
