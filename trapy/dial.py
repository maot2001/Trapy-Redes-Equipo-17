from trapy import *
from utils import *
from flags import *


def send_Test_pack(addr:str,flags:Flags,data:bytes=b''):
    print('Comienza a ejecuatrse el dial en:',addr)
    conn=dial(addr)
    print('Dial ejecuatado en:',conn.origin_address)
    print("Entrando a el send")
    send(conn,data)
    print('Paquete enviado')
    
    
flags=Flags()
flags.SYN=0
word =str([i for i in range(0,10)])
data=b'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiinmvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv,'
addr="127.68.0.10:5000"
send_Test_pack(addr,flags,data)
