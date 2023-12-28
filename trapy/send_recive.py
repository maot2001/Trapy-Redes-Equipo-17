
from conn import *
import logging
import time
import random
import threading
from utils import *
from conn import *
from _send import send as sends
from recive_utils import *


class wrapped_conn:
    
    def __init__(self):
       
        self.buffer=[]
        self.max_buffer_size=1024
        
        
    def push(self,data:bytes,addr):
        
        self.buffer.append(data)
        
    def pop(self):
        if len(self.buffer)==0:
            return None
        return self.buffer.pop(0)

class Recive:
    
    def __init__(self,conn:Conn):
        self.conn=conn
        self.buffer=[]
        self.max_buffer_size=1024
        
    def recibe(self):
        
        self.buffer.append(self.recv(self.conn,self.max_buffer_size))
        

    def get_bytes_in_index(self,index:int)->bytes:
        return self.buffer[index]
        
        
        
        
        
        
    def recv(conn: Conn, length: int) -> bytes:

        r=False


        mss:int=1024    
        #TODO: Añadir que el tamaño de ventana tiene que ser <= length restante    
        #TODO:Añadir en caso que el window lengh es > length hay que corregirlo
        buffer:list=[]
        buffer_length:int=0
        i=0
        while True:
            i+=1
            packet, _ = conn.socket.recvfrom(mss)
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
                conn.socket.sendto(packet,conn.connected_address[0])
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

            return join_byte_arrays(buffer)



class Send:
    

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
                     conn.socket.sendto(packet,d_addr)

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
                         packet, _ = conn.socket.recvfrom(mss)

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

                #Esperar el acuse de recibo
        #Cerrar conexión
        #Envio mi petición de cierre de conexión
        """
        flags=Flags()
        flags.FIN=1
        packet=create_packet(conn,0,flags)
        conn.socket.sendto(packet,conn.connected_address[0])
        ##Leer si me mandaron el ack
        packet, _ = conn.socket.recvfrom(mss)
        address, protocol, data, flags = data_conn(packet)
        tcp_header=Protocol_Wrapped(protocol)
        if(flags.ACK and flags.FIN):
            print('Se recibio un paquete de FIN-ACK')
            conn.refresh(0,convert_bytes_to_int(tcp_header.ack_num),convert_bytes_to_int(tcp_header.seq_num),0) 
            flags=Flags()
            flags.ACK=1
            packet=create_packet(conn,0,flags)
            conn.socket.sendto(packet,conn.connected_address[0])
            print('Se envio un el paquete que dice que se recibio el ACK-FIN, se cierra la conexion')
            #TODO:Cerrar conexion
            """