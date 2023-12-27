from converters_utils import parse_address, address_to_bytes
from utils import *
from conn import *

logger = logging.getLogger(__name__)



def listen(address: str,max_conn:int=10)->Conn:
    
    addr,port=parse_address(address)
    addr_b=address_to_bytes(addr)
    port_b=int_to_bytes(port,2)
    
    tcp_header=TCP_Header(source_address=addr_b,port_source=port_b,flags=Flags())
    conn = Conn(tcp_header=tcp_header,is_server=True)
    #Ahora esta en modo servidor
   # conn.origin_address = parse_address(address)
    conn.connected_bounds=[None for _ in range(max_conn - 1)]
  

    return conn


def accept(conn: Conn):
    
        return conn.data_conn_Acept()

        


def dial(address: str)->Conn:
 pass
#maje

def send(conn: Conn, data: bytes) -> int:
    pass
def recv(conn: Conn, length: int) -> bytes:

   pass


def close(conn: Conn):
    conn.socket.close()
    logger.info(f'close connection')
    conn.socket = None




dial("127.0.0.1:8000")
