from trapy import *
from utils import *
from flags import *


def send_Test_pack(addr:str,flags:Flags,data:bytes=b''):
    print('Comienza a ejecuatrse el dial en:',addr)
    conn=dial(addr)
    print('Dial ejecuatado en:',conn.origin_address)
    packet=create_packet(conn,0,flags,data)

    conn.socket.sendto(packet, conn.connected_address[0])
    print('Paquete enviado')
    
flags=Flags()
flags.SYN=0
data=b'hola'
addr="127.68.0.10:5000"
send_Test_pack(addr,flags,data)
