import logging

from converters_utils import  calculate_checksum

AUX = (1 << 16) - 1

# Configura el logger para que registre los mensajes en un archivo
logging.basicConfig(filename='app.log', level=logging.INFO)


def get_bytes(protocol, init, end):
    return int.from_bytes(protocol[init : end], byteorder = 'big', signed = False)


def hex(arr):
    count = 0
    for i in range(0, len(arr), 2):
        count += int.from_bytes(arr[i : min(i + 2, len(arr))], byteorder = 'big', signed = False)
    return count & AUX





import struct

def verify_ip_checksum(ip_header:bytes):
    """_summary_
    Este código define una función verify_ip_checksum() que toma una cabecera IP
    en bytes como argumento. Desempaqueta la cabecera IP, obtiene el checksum de la
    cabecera IP, crea una versión de la cabecera IP con el checksum a cero, calcula 
    el checksum y comprueba si el checksum recibido es igual al checksum calculado
    . 
    Args:
        ip_header (bytes): _description_

    Returns:
        Bool: Devuelve True si el checksum es correcto y False en caso contrario.
    """
    # Desempaqueta la cabecera IP
    unpacked_ip_header = struct.unpack('!BBHHHBBH4s4s', ip_header)

    # Obtiene el checksum de la cabecera IP
    received_checksum = unpacked_ip_header[5]

    # Crea una versión de la cabecera IP con el checksum a cero
    zeroed_ip_header = struct.pack('!BBHHHBBH4s4s', *unpacked_ip_header[:5], 0, *unpacked_ip_header[6:])

    # Calcula el checksum
    calculated_checksum = 0
    for i in range(0, len(zeroed_ip_header), 2):
        calculated_checksum += (zeroed_ip_header[i] << 8) + zeroed_ip_header[i+1]
    calculated_checksum = (calculated_checksum >> 16) + (calculated_checksum & 0xffff)
    calculated_checksum += calculated_checksum >> 16
    calculated_checksum = ~calculated_checksum & 0xffff

    # Comprueba si el checksum recibido es igual al checksum calculado
    return received_checksum == calculated_checksum


def verify_tcp_checksum(tcp_header:bytes):
    """_summary_
    Este código define una función verify_tcp_checksum() que toma una cabecera 
    TCP en bytes como argumento. Desempaqueta la cabecera TCP, obtiene el checksum
    de la cabecera TCP, crea una versión de la cabecera TCP con el checksum a cero,
    calcula el checksum y comprueba si el checksum recibido es igual al checksum calculado.
    

    Args:
        tcp_header (bytes): Cabecera Tcp

    Returns:
        Bool: Devuelve True si el checksum es correcto y False en caso contrario.
    """
    # Desempaqueta la cabecera TCP
    unpacked_tcp_header = struct.unpack('!HHLLBBHHH', tcp_header)

    # Obtiene el checksum de la cabecera TCP
    received_checksum = unpacked_tcp_header[6]

    # Crea una versión de la cabecera TCP con el checksum a cero
    zeroed_tcp_header = struct.pack('!HHLLBBHHH', *unpacked_tcp_header[:6], 0, *unpacked_tcp_header[7:])

    # Calcula el checksum
    calculated_checksum = 0
    for i in range(0, len(zeroed_tcp_header), 2):
        calculated_checksum += (zeroed_tcp_header[i] << 8) + zeroed_tcp_header[i+1]
    calculated_checksum = (calculated_checksum >> 16) + (calculated_checksum & 0xffff)
    calculated_checksum += calculated_checksum >> 16
    calculated_checksum = ~calculated_checksum & 0xffff

    # Comprueba si el checksum recibido es igual al checksum calculado
    return received_checksum == calculated_checksum

def make_frames(data:bytes,size:int)->list:
     return[data[i:min(len(data),i + 1024)]for i in range(0,len(data),1024)]
 
 #TODO:Make New

def int_to_bytes(number, size:int)->bytes:
    """
    Converts an integer to a byte array of the specified size.
    
    Args:
        number (int): The integer to convert.
        size (int): The size of the resulting byte array.
        
    Returns:
        bytes: The byte array representation of the integer.
    """

    return number.to_bytes(size, byteorder='big', signed=False)

def make_ip_header(source_ip, destination_ip):
        ip_header = b'\x45\x00\x00\x28'  # Version, IHL, Type of Service | Total Length
        ip_header += b'\xab\xcd\x00\x00'  # Identification | Flags, Fragment Offset
        ip_header += b'\x40\x06\xa6\xec'  # TTL, Protocol | Header Checksum   xff en protocol
        source_ip = [int(i) for i in source_ip.split('.')]
        destination_ip = [int(i) for i in destination_ip.split('.')]
        ip_header += bytes(source_ip)  # Source Address
        ip_header += bytes(destination_ip)  # Destination Address
        return ip_header

def calculate_checksum(data,tcp_header):
        checksum = hex(data) + hex(tcp_header)
        checksum = AUX - (checksum & AUX)
        return checksum.to_bytes(2, byteorder='big', signed=False)
    
def make_protocol_header(source_port, destination_port, seqnumber, acknumber, window_size, ACK = 0, SYN = 0, FIN = 0, data = b''):
        tcp_header = int_to_bytes(source_port, 2) # Source Port
        tcp_header += int_to_bytes(destination_port, 2)  # Destination Port
        tcp_header += int_to_bytes(seqnumber, 4)  # Sequence Number
        tcp_header += int_to_bytes(acknumber, 4)  # Acknowledgement Number
        tcp_header += int_to_bytes(((ACK << 4) + (SYN << 1) + (FIN)), 2)# Flags
        tcp_header += int_to_bytes(window_size, 2) # Window Size
        tcp_header += b'\x00\x00\x00\x00'  # Checksum | Urgent Pointer
    
        checksum= calculate_checksum(data, tcp_header)
        
        tcp_header = tcp_header[:16] + checksum + tcp_header[18:]
        return tcp_header + data





def unpack(packet:bytes):
    """
    Desempaqueta un paquete de bytes en sus componentes principales: cabecera IP, cabecera TCP y datos.
    
    Args:
        packet (bytes): El paquete de bytes a desempaquetar.
    
    Returns:
        tuple: Una tupla que contiene la cabecera IP, la cabecera TCP y los datos del paquete.
               Si el paquete es demasiado pequeño o los checksums son inválidos, se devuelve None.
    """
  
    if(len(packet)<40):
        # Si es menor de 40 bytes no se puede desempaquetar
        # la trama está dañada
        logging.error(f"Imposible desempaquetar, demasiado pequeño({len(packet)})")
        return None
    
    ip_header, tcp_header, data = packet[0:20], packet[20:40], packet[40:]
    
    # Chequear el checksum del IP
    if(not verify_ip_checksum(ip_header)):
        logging.error(f"Checksum inválido del IP")
        return None
    
    # Chequear el checksum del TCP
    if(not verify_tcp_checksum(tcp_header)):
        logging.error(f"Checksum inválido del TCP")
        return None
    
    tcp_header_Wrapped= Get_TCP_Header_From_IP_TCP_Headers(ip_header=ip_header, tcp_header=tcp_header)
    
    return  tcp_header_Wrapped, data


"""
def end(conn : Conn, packet):
    if not packet:
        packet = create_packet(conn, FIN = 1, ACK = 1)
    
    conn.time_mark = time.time()
    
    while True:
        if not conn.running() or conn.timeout():
            conn.time_mark = time.time()
            conn.socket.sendto(packet, conn.connected_address)
        
        if conn.waiter(30):
            conn.stop()
            return
        
        try:
            _, protocol, _ = data_conn(conn)
        except:
            continue

        if get_bytes(protocol, 4, 8) != conn.ack or get_bytes(protocol, 8, 12) != conn.seq + 1 or not protocol[13] == 1 or \
            not protocol[14] == 1:
            pass
        else:
            conn.stop()
            conn.refresh(protocol)
            break
            """