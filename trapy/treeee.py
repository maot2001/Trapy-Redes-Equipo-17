       

from conn import *
import logging
import time
import random
import threading
from utils import *
from conn import *
from _send import send as sends
from recive_utils import *

conn1=Conn()
conn1.origin_address=("127.0.68.2",5000)
conn1.connected_address.append(("127.0.0.1",1))
conn1.ack.append(int_to_bytes(100,4))
conn1.seq.append(int_to_bytes(100,4))
def recv( packet ,length: int) -> bytes:
         
        conn=conn1

        mss:int=1024    
        #TODO: Añadir que el tamaño de ventana tiene que ser <= length restante    
        #TODO:Añadir en caso que el window lengh es > length hay que corregirlo
        buffer:list=[]
        buffer_length:int=0
        i=0
        while True:
            i+=1
           # packet, _ = conn.socket.recvfrom(mss)
            address, protocol, data, flags = data_conn(packet)
            assert len(data)==4,f'El tamaño del paquete no es el esperado, se espera : {48} y se recibe {len(data)}'
            #Si es acuse de recibo continuar

            """
            Momentáneamente si el ACK=1 => que es un mensaje de confirmación de algún tipo
            """
            #Si es un paquete de datos con este flag lo ignoro que vuelva a reenviarlo bien
            if(flags.SYN):
                continue
            
            if(flags.ACK):
                continue
            new_data_length=len(data)

            tcp_header=Protocol_Wrapped(protocol)
            #Se procede a inicial el cierre de conexion
            if(flags.FIN):
                print('Se recibio un paquete de fin')
                conn.refresh(0,convert_bytes_to_int(tcp_header.ack_num),convert_bytes_to_int(tcp_header.seq_num),1) 
                flags=Flags()
                flags.FIN=1
                flags.ACK=1
                packet=create_packet(conn,0,flags)
                #conn.socket.sendto(packet,conn.connected_address[0])
                print('Se envio un paquete de FIN-ACK')


            #Si el tamaño del paquete es mayor al tamaño de la ventana
            if(buffer_length+new_data_length>length):
               continue
           #TODO:Por decidir si espero su nuevos bytes o trunco
           #POr defecto esta esperar

            buffer.append(data)
            buffer_length+=new_data_length


            #SI llego a su maxima capacidad de ventana
            if(buffer_length+new_data_length==length):
                return join_byte_arrays(buffer) 


            index = conn.connected_address.index(address)
            ack_packet_response(conn,index,new_data_length)
            print('Se envio un paquete de ACK Hacia el SEND con ask: ',conn)
            return packet
            #return join_byte_arrays(buffer)

conn2=Conn()
conn2.origin_address=("127.0.0.1",1)
conn2.connected_address.append(("127.0.68.2",5000))
conn2.ack.append(int_to_bytes(100,4))
conn2.seq.append(int_to_bytes(100,4))

def send(conn: Conn, data: bytes) -> int:

        mss:int=1024
        windows_length=conn.windows_length
        buffer=bytes_buffer(data)
        #Mientras que haya que enviar
         #TODO:Implementar pipeline
        j=1
        while len(buffer)>0 :
            #TODO: Suponer que es solo un un cliente por ahora
            for i in range(len(conn.connected_address)):
                a=0
                while True:   
                     a+=1
                     d_addr=conn.connected_address[i]
                     flags=Flags()

                     #Datos a enviar en esta iteración
                     send_data=buffer.get_count_bytes(windows_length)

                     #Crear el paquete
                     packet=create_packet(conn,i,flags,send_data)

                     #enviar 
                     ack= recv(packet,len(send_data))
                    # conn.socket.sendto(packet,d_addr)

                     #tamaño de los datos enviados solo los datos no incluye cabeceras

                     data_length:int=len(send_data)
                     #TODO: despues poner los setTimeOut
                     #time.sleep(1)

                     ii=0
                     while True:
                         ii+=1
                         if(ii>10):
                             print("No se recibio a tiempo el ack esperado-------------------")
                             break
                         #TODO: Poner el timeout
                         #packet, _ = conn.socket.recvfrom(mss)
                         packet=ack
                        # assert Is_the_packet_for_me(packet,d_addr),f'El paquete no es para mi'
                         if(Is_the_packet_for_me(packet,d_addr)):
                                 print("JJJJJJJJJJJJJJJKK")
                                 address, protocol, data, flags = data_conn(packet)
                                 tcp_header=Protocol_Wrapped(protocol)

                                 rec_ack=convert_bytes_to_int(tcp_header.ack_num)
                                 seq=convert_bytes_to_int(conn.seq[i])

                                 ack=convert_bytes_to_int(conn.ack[i])
                                 #Si tiene el ack y el seq+cant bytes enviados es = al ack number del paquete ack

                                 assert  rec_ack ==ack+data_length,f"No es el ack esperado, esperado:{ack}, recibido {rec_ack} en la iteración{a}"
                                 assert flags.ACK ,f'el flag debe ACK no esta 1'
                                 assert  flags.SYN==0,f'el flag debe SYN no esta 0'
                                 if(flags.ACK and rec_ack ==  ack+data_length):
                                     print('Se recibio un paquete de ACK, aca')
                                     break
                       #TODO:AÑadir si es para desconectar

            print('Se envio un paquete')  

send(conn2,b'holas')     
            
            

class Connn:
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

    def __init__(self, sock=None):
        self.origin_address: tuple[str, int] = None

        """
        Aqui van los datos de todas la conexiones q estan establecidas con el origin_address
        
        Se debe acceder a los datos de cada una por el indice asociado al connected_address, con este se puede saber los valores
        de ack y seq, con nombre.connected_address.index(address) tienen ese indice, address deben recibirlo de data_conn luego
        de separar la info del paquete recibido
        
        Para comprobar la existencia de address en connected_address pueden usar: if address in connected_address y asi evitar
        errores de mensajes

        No me queda claro que el proyecto necesite estas listas de conexiones, creo que las conexiones de un origen con varios
        destinos podria representarse como varios conn, pero para el send y recv no se que les sera mas comodo

        En accept hice un comentario sobre el tipado de self.ack y sel.seq
        """
        self.connected_address: list(tuple[str, int]) = []
        self.ack: list(bytes) = []
        self.seq: list(bytes) = []
        
        self.windows_length = 4

        if sock == None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.socket = sock

    def refresh(self, index: int, new_ack: int, new_seq: int, data: int):
        """
        Este metodo les permite modificar los ack y seq pasando el tamaño del paquete recibido, ahora mismo todos los valores
        son int, pero puede hacerse con bytes o con lo que sea, la idea no cambia
        """
        self.seq[index] = new_ack.to_bytes(4,byteorder='big', signed=False)
        new_seq += data
        self.ack[index] = new_seq.to_bytes(4,byteorder='big', signed=False)

    
    def refresh_(self,index:int,data_length:int):
        h_ack= int.from_bytes(self.ack[-1],byteorder='big', signed=False)
        h_seq= int.from_bytes(self.seq[-1],byteorder='big', signed=False)
        self.refresh(index,h_ack,h_seq+data_length,0)

 