

from utils import *

from trapy import *

def recv_Test_pack(addr:str):
    print('Comienza a ejecuatrse el listen en:',addr)
    conn=listen("127.68.0.10:5000")
    print("server listening")
    accept(conn)

    print("server accepted connection")
    print("Listo para recibir")
    print('Se recibió',recv(conn, 1024))

    print('Terminado el Recive')
    
    


addr="127.68.0.10:5000"
recv_Test_pack(addr)