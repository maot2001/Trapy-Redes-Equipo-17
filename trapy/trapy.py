import logging
import time
import random
import threading
from utils import *
from conn import *
from _send import send as sends

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
            print("server receiving ack from client")
            print("three handshake complete")
            #Ya se establecio la conexion, tree handshake completado, luego se actualizan los valores de ack y seq en el server
            conn.refresh(index, int.from_bytes(protocol[8:12], byteorder='big', signed=False), int.from_bytes(protocol[4:8], byteorder='big', signed=False), 0)
            return conn

def dial(address: str) -> Conn:
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
        print("client sending ack to server")
        conn.socket.sendto(packet, conn.connected_address[index])
        #Se envia y se termina el tree handshake (debo poner las rectificaciones de si no llegan y cosas x el estilo)
        break
    return conn
    #esto es para sacar la conexion del cliente del hilo
from recive_utils import *

def send(conn: Conn, data: bytes) -> int:

    mss:int=1024
    windows_length=conn.windows_length
    buffer=bytes_buffer(data)
    
    my_ack=conn.ack[0]
    my_seq=conn.seq[0]
    
    #cabiar a 1 mi ack
    #mi sq
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
                     if(Is_the_packet_for_me(packet,conn.origin_address)):
                             print("JJJJJJJJJJJJJJJKK")
                             address, protocol, data, flags = data_conn(packet)
                             tcp_header=Protocol_Wrapped(protocol)

                             rec_ack=convert_bytes_to_int(tcp_header.ack_num)
                             rec_seq=convert_bytes_to_int(tcp_header.seq_num)
                             seq=convert_bytes_to_int(conn.seq[i])
                             import os

# Limpiar la consola
                             os.system('cls' if os.name == 'nt' else 'clear') 
                             ack=convert_bytes_to_int(conn.ack[i])
                             print("Se recibio un paquete de ACK")
                             print('mi ack',convert_bytes_to_int(my_ack))
                             print('mi seq',convert_bytes_to_int(my_seq))
                             print('el ack recibido',rec_ack)
                             print('el seq recibido',rec_seq)       
                             my_ack=convert_bytes_to_int(my_ack)
                             #Si tiene el ack y el seq+cant bytes enviados es = al ack number del paquete ack

                             assert  rec_seq ==my_ack+data_length,f"No es el ack esperado, esperado:{ack}, recibido {rec_ack} en la iteración{a} con dalta{data_length}"
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





def recv(conn: Conn, length: int) -> bytes:
    
    r=False
    my_ack=conn.ack[0]
    my_seq=conn.seq[0]
    
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
        ack_packet_response(tcp_header,conn,index,new_data_length)
        print('Se envio un paquete de ACK Hacia el SEND con ask: ',conn)
    
        return join_byte_arrays(buffer)


def close(conn: Conn):
    conn.socket.close()
    logger.info(f'close connection')
    conn.socket = None