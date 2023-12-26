from flags import Flags
from converters_utils import bytes_to_int, int_to_bytes, calculate_checksum


class TCP_Header:
     
    def __init__(self,source_address,
                 port_source:bytes,
                 flags:Flags
                 ,destination_address=None,
                 ack_number:bytes=None#32 bits
                 ,seq_number:bytes=None, #32 bits
                 port_destination:bytes=None,
                 recv_window:bytes=None
         
                 ) :
        #source addr
        self.source_address:bytes = source_address
        self.port_source:bytes=port_source
        #dest addr
        self.destination_address:bytes = destination_address
        self.port_destination:bytes=port_destination
       
        self.ack_number: bytes =ack_number
        self.seq_number: bytes =seq_number
        self.flags:Flags=flags
        
        
        self.recv_window=recv_window
        
   
    
    def __get_address_from_bytes_to_str(address:bytes) -> str:
   
        return ".".join(str(byte) for byte in address)    


    def get_address_source_to_str(self):
       return self.get_address_from_bytes_to_str(self.source_address)
      
    def get_address_destination_to_str(self):
       return self.get_address_from_bytes_to_str(self.destination_address)  
    
    def get_property_from_bytes_to_int(data:bytes):
             
        return int.from_bytes(data, "big")
    
    def set_source_address(self,address:bytes):
        self.source_address=address
    
    def set_source_port(self,port:bytes):
        self.port_source=port
        
    def refesh_seq(self):
        """
        Refreshes the sequence number by adding 1 to the current sequence number.
        """
        self.add_seq(1)
        
        
        
    def add_seq(self, add: int):
        """
        Incrementa el número de secuencia en la cantidad especificada.

        :param add: La cantidad a incrementar el número de secuencia.
        :type add: int
        """
        # Convertir seq_number de bytes a entero
        seq_number_int = bytes_to_int(self.seq_number)

        # Incrementar seq_number_int en 1
        seq_number_int += add

        # Convertir seq_number_int de nuevo a bytes
        self.seq_number = int_to_bytes(seq_number_int, 32)
        
        
    def refesh_ack(self):
        """
        Refreshes the acknowledgement number by adding 1 to the current value.
        """
        self.add_ack(1)
        
    def add_ack(self, add: int):
        """
        Adds the specified value to the current ACK number.

        Parameters:
        add (int): The value to be added to the ACK number.

        Returns:
        None
        """
        ack_number_int = bytes_to_int(self.ack_number)
        
        ack_number_int += add
        
        self.ack_number = int_to_bytes(ack_number_int, 32)
    def add_ack(self,add:int):
        ack_number_int = bytes_to_int(self.ack_number)
        
        ack_number_int+=add
        
        self.ack_number=int_to_bytes(ack_number_int,32)
          
    def set_seq_num(self,seq_number:bytes):
        self.seq_number=seq_number
        
    def set_ack_num(self,ack_number:bytes):
        self.ack_number=ack_number
        
        
    def __set_port_from_int(port:int)->bytes:
        return port.to_bytes(2, "big")
        
    def set_port_source_from_int(self,port:int):
        self.port_source=self.__set_port_from_int(port)
    
    def set_port_destination_from_int(self,port:int):
        self.port_destination=self.__set_port_from_int(port)
    
    
    
    def __msg_from_int(msg:int)->bytes:
        return msg.to_bytes(4, "big")
    
    def set_ack_from_int(self,ack:int):
        self.ack_number=self.msg_from_int(ack)
    
    def set_seq_number_from_int(self,seq_num:int):
        self.seq_number=self.msg_from_int(seq_num)
        
    def recive_windows_from_int(self,windows:int):
        self.recv_window= windows.to_bytes(2, "big")
        
        
        
    def create_tcp_header_to_bytes(self, seq_number: int = -1, flags: Flags = None) -> bytes:
            """
            Converts the TCP header to bytes.

            Args:
                seq_number (int, optional): The sequence number. Defaults to -1.
                flags (Flags, optional): The TCP flags. Defaults to None.

            Returns:
                bytes: The TCP header as bytes.
            """
            if seq_number != -1:
                seq_number = self.set_seq_number_from_int(seq_number)
            else:
                seq_number = self.seq_number

            if flags == None:
                self.flags = flags

            tcp_header = self.port_source
            tcp_header += self.port_destination
            tcp_header += self.seq_number
            tcp_header += self.ack_number
            tcp_header += b"\x50"
            tcp_header += self.flags.to_bytes(True)
            tcp_header += self.recv_window
            tcp_header += calculate_checksum(tcp_header)
            tcp_header += b"\x00\x00"

            return tcp_header
    def create_tcp_header_to_bytes(self,seq_number:int=-1,flags:Flags=None):
        if seq_number!=-1:
           seq_number= self.set_seq_number_from_int(seq_number)
        else:
            seq_number=self.seq_number
            
        if flags==None:
            self.flags=flags
        tcp_header =self.port_source 
        tcp_header+=self.port_destination 
        tcp_header+= self.seq_number 
        tcp_header+= self.ack_number
        tcp_header+=b"\x50" 
        tcp_header+= self.flags.to_bytes(True)
        tcp_header+= self.recv_window
        tcp_header+=calculate_checksum(tcp_header)
        tcp_header += b"\x00\x00"
        return tcp_header
    
    
def Get_TCP_Header_From_IP_TCP_Headers(ip_header:bytes,tcp_header:bytes)->TCP_Header:
        """
        This function extracts TCP header information from IP and TCP headers.

        Parameters:
        ip_header (bytes): The IP header.
        tcp_header (bytes): The TCP header.

        Returns:
        TCP_Header: An object containing the extracted TCP header information.
        """
        #Ips address
        addr_source=ip_header[12:16]
        addr_dest=ip_header[16:20]
        #Ports
        source_port = tcp_header[0:2]
        dest_port = tcp_header[2:4]
        #seq and ack number
        secnumber = tcp_header[4:8]
        acknumber =tcp_header[8:12]

        #flags
        flags = Flags()
        flags.from_bytes_to_flags(tcp_header[13])

        #windows size
        recv_window = tcp_header[14:16]

        tcp_header=TCP_Header(source_address=addr_source,
                            destination_address=addr_dest,
                            port_source=source_port,
                            port_destination=dest_port,
                            seq_number=secnumber,
                            ack_number=acknumber,
                            flags=flags,
                            recv_window=recv_window)

        return tcp_header