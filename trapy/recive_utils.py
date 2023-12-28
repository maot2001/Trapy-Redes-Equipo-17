from utils import *

def join_byte_arrays(byte_arrays)->bytes:
    """
    Combines multiple byte arrays into a single byte array.

    Args:
        byte_arrays (list): A list of byte arrays.

    Returns:
        bytes: The combined byte array.

    Raises:
        AssertionError: If the input list is empty.
    """
    flattened = [ item for item in byte_arrays]
    assert len(flattened)>0,"No hay nada que unir"
    if len(flattened)<1: return None
    temp=flattened[0]
    print(temp,'temp')
    for i in flattened[1:]:
        temp+=i
    return temp


def join_byte_arrays_of_arrays(byte_arrays)->bytes:
    """
    Combina una lista de listas de arrays de bytes en un solo array de bytes.

    Args:
        byte_arrays (list): Una lista de listas de arrays de bytes.

    Returns:
        bytes: El array de bytes resultante de la combinación de las listas.

    Raises:
        AssertionError: Si la lista de listas está vacía.
    """
    # Aplanar la lista de listas en una sola lista
    flattened = [item for sublist in byte_arrays for item in sublist]
    assert len(flattened)>0,"No hay nada que unir"
    if len(flattened)<1: return None
    temp=flattened[0]
    print(temp,'temp')
    for i in flattened[1:]:
        temp+=i
    # Unir todos los arrays de bytes en uno solo
    return temp

def get_new_seq_num_and_ack(self, index: int, old_ack: int, old_seq: int, data_length: int):
        """
        Este metodo les permite modificar los ack y seq pasando el tamaño del paquete recibido, ahora mismo todos los valores
        son int, pero puede hacerse con bytes o con lo que sea, la idea no cambia
        """
        self.seq[index] = old_ack.to_bytes(4,byteorder='big', signed=False)
        old_seq += data_length
        self.ack[index] = old_seq.to_bytes(4,byteorder='big', signed=False)



class Protocol_Wrapped:
    
    def __init__(self,protocol:bytes):
        self.protocol=protocol
        self.o_port=protocol[0:2]
        self.d_port=protocol[2:4]
        self.seq_num=protocol[4:8]
        self.ack_num=protocol[8:12]
        self.window_size=protocol[14:16]
        
    


def convert_bytes_to_int(data:bytes):
    return int.from_bytes(data,byteorder='big', signed=False)


def ack_packet_response(conn,index,tcp_header,new_date_l:int)->bool:
    h_ack=convert_bytes_to_int(tcp_header.ack_num)
    h_seq=convert_bytes_to_int(tcp_header.seq_num)
    conn.refresh(index,h_ack,h_seq,new_date_l)
    flags:flags=Flags()
    flags.ACK=1 
    packet=create_packet(conn,index,flags)
    conn.socket.sendto(packet, conn.connected_address[index])
    return True




class bytes_buffer():
    def __init__(self,data:bytes):
        
        self.buffer=[ data[i:i+1] for i in range(0,len(data))]
        self.buffer.reverse()
        
    def pop(self)->bytes:
        if self.buffer:
         assert len(self.buffer)>0,"buffer is empty"
         return self.buffer.pop()
    
    def pop_count(self,count:int):
        return [self.buffer.pop() for _ in range(min(len(self.buffer),count))]
    
    def get_count_bytes(self,count:int)->bytes:
         a=self.pop()
         for i in self.pop_count(count-1):
             a+=i
         return a
    
    
    def __len__(self):
        return len(self.buffer)


