from utils import *
def join_byte_arrays(byte_arrays):
    # Aplanar la lista de listas en una sola lista
    flattened = [item for sublist in byte_arrays for item in sublist]
    
    # Unir todos los arrays de bytes en uno solo
    return b''.join(flattened)

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
    flags=flags()
    flags.ACK=1 
    packet=create_packet(conn,index,flags)
    conn.socket.sendto(packet, conn.connected_address[index])
    return True