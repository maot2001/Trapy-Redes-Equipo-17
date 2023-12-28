
from utils import *

from trapy import *

import asyncio


import threading

flags=Flags()
flags.SYN=0
data=b'holo mundo'
addr="127.68.0.10:5000"

def send_Test_pack(addr:str,flags:Flags,data:bytes=b''):
    print('Comienza a ejecuatrse el dial en:',addr)
    conn=dial(addr)
    print('Dial ejecuatado en:',conn.origin_address)
    send(conn,data)
    print('Paquete enviado')
    
    
def recv_Test_pack(addr:str):
    print('Comienza a ejecuatrse el listen en:',addr)
    conn=listen("127.68.0.10:5000")
    print("server listening")
    accept(conn)

    print("server accepted connection")
    print("Listo para recibir")
    print(f' Valor del recv : {recv(conn, 1024)}')
    print('Terminado el Recive')

# Crear un bucle de eventos
# = asyncio.get_event_loop()

# Ejecutar las tareas de forma asíncrona
#loop.run_until_complete(asyncio.gather(send_Test_pack(addr,flags,data),recv_Test_pack(addr)))

# Crear hilos para las funciones
thread1 = threading.Thread(target=send_Test_pack, args=(addr,flags,data))
thread2 = threading.Thread(target=recv_Test_pack, args=(addr,))

# Iniciar los hilos
thread2.start()
thread1.start()
# Esperar a que ambos hilos terminen
thread1.join()
thread2.join()