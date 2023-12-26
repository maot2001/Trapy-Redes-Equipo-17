from conn import Conn
import flags
AUX = (1 << 16) - 1


def parse_address(address):
    host, port = address.split(':')

    if host == '':
        host = 'localhost'

    return host, int(port)


def get_bytes(protocol, init, end):
    return int.from_bytes(protocol[init : end], byteorder = 'big', signed = False)


def hex(arr):
    count = 0
    for i in range(0, len(arr), 2):
        count += int.from_bytes(arr[i : min(i + 2, len(arr))], byteorder = 'big', signed = False)
    return count & AUX




def build_iph(origin_ip, connected_ip):
    ip_header = b'\x45\x00\x00\x28'  # Version, IHL, Type of Service | Total Length
    ip_header += b'\xab\xcd\x00\x00'  # Identification | Flags, Fragment Offset
    ip_header += b'\x40\x06\xa6\xec'  # TTL, Protocol | Header Checksum   xff en protocol
    origin_ip = [int(i) for i in origin_ip.split('.')]
    connected_ip = [int(i) for i in connected_ip.split('.')]
    ip_header += bytes(origin_ip)  # Source Address
    ip_header += bytes(connected_ip)  # Destination Address
    return ip_header


def build_protocolh(o_port, c_port, seq, ack, windows_length, ACK = 0, SYN = 0, FIN = 0, data = b''):
    tcp_header = o_port.to_bytes(2, byteorder = 'big', signed = False)  # Source Port
    tcp_header += c_port.to_bytes(2, byteorder = 'big', signed = False)  # Destination Port
    tcp_header += seq.to_bytes(4, byteorder = 'big', signed = False)  # Sequence Number
    tcp_header += ack.to_bytes(4, byteorder = 'big', signed = False)  # Acknowledgement Number
    tcp_header += ((ACK << 4) + (SYN << 1) + (FIN)).to_bytes(2, byteorder = 'big', signed = False)  # Flags
    tcp_header += windows_length.to_bytes(2, byteorder = 'big', signed = False)  # Window Size
    tcp_header += b'\x00\x00\x00\x00'  # Checksum | Urgent Pointer

    checksum = hex(data) + hex(tcp_header)
    checksum = AUX - (checksum & AUX)
    checksum = checksum.to_bytes(2, byteorder = 'big', signed = False)

    tcp_header = tcp_header[:16] + checksum + tcp_header[18:]
    return tcp_header + data


def create_packet(conn : Conn, seq = -1, ack = -1, ACK = 0, SYN = 0, FIN = 0, data = b''):
    o_addr, o_port = conn.origin_address
    c_addr, c_port = conn.connected_address

    if c_addr == 'localhost':
        c_addr, c_port = conn.socket.getsockname()

    ip_header = build_iph(o_addr, c_addr)
    #TODO: Hay que hacer esto desde que se crea el objeto COnn
   # if seq == -1: seq = conn.seq
    if seq ==-1 : seq=1
    if ack == -1: ack = conn.ack
    
    protocol_header = build_protocolh(o_port, c_port, seq, ack, conn.windows_length, ACK, SYN, FIN, data)
    return ip_header + protocol_header


def corrupt(protocol, data):
    recv_checksum = int.from_bytes(protocol[16:18], byteorder = 'big', signed = False)
    
    protocol_aux = protocol[:16]
    protocol += b'\x00\x00\x00\x00'
    
    exp_checksum = hex(data) + hex(protocol_aux)
    exp_checksum = AUX - (exp_checksum & AUX)
    return recv_checksum != exp_checksum


def data_conn(conn : Conn):
    try:
        packet, _ = conn.socket.recvfrom(1024)
    except:
        return None

    ip_header, protocol, data = packet[20:40], packet[40:60], packet[60:]

    if corrupt(protocol , data):
        return None
    
    ip = '.'.join(map(str, ip_header[12:16]))
    port = int.from_bytes(protocol[:2], byteorder='big', signed=False)

    return ((ip, port), protocol, data)



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
        tcp_header = int_to_bytes(source_port,2) # Source Port
        tcp_header += int_to_bytes(destination_port,2)  # Destination Port
        tcp_header += int_to_bytes(seqnumber,4)  # Sequence Number
        tcp_header += int_to_bytes(acknumber,4)  # Acknowledgement Number
        tcp_header += int_to_bytes(((ACK<<4) + (SYN << 1) + (FIN)) ,2)# Flags
        tcp_header +=int_to_bytes(window_size,2) # Window Size
        tcp_header += b'\x00\x00\x00\x00'  # Checksum | Urgent Pointer
    
        checksum=calculate_checksum(data,tcp_header)
        
        tcp_header = tcp_header[:16] + checksum + tcp_header[18:]
        return tcp_header + data



#TODO:ADD From Marcos
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