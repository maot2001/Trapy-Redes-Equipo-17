from flags import Flags


        

class TCP_Header:
     
    def __init__(self,origin_address,
                 flags:Flags
                 ,connected_address=None,
                 ack_number:bytes=None
                 ,seq_number:bytes=None,
                 port_source:bytes=None,
                 port_destination:bytes=None,
                 recv_window:bytes=None
                 ) :
        self.origin_address:bytes = origin_address
        self.connected_address:bytes = connected_address
        self.ack_number: bytes =ack_number
        self.seq_number: bytes =seq_number
        self.flags:Flags=flags
        self.port_source:bytes=port_source
        self.port_destination:bytes=port_destination
        self.recv_window=recv_window
        
   
    
    def get_address_from_bytes_to_str(self,address:bytes) -> str:
   
        return ".".join(str(byte) for byte in address)    


    def get_address_source_to_str(self):
       return self.get_address_from_bytes_to_str(self.origin_address)
      
    def get_address_destination_to_str(self):
       return self.get_address_from_bytes_to_str(self.connected_address)  
    
    def get_property_from_bytes_to_int(data:bytes):
             
        return int.from_bytes(data, "big")