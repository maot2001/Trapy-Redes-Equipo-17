import socket
import time
from utils import get_bytes


class Conn:
    """
    Esta es la clase Conn. Aquí puedes describir la clase.

    Atributos
    ---------
    origin_address : type
        Descripción de origin_address.
    connected_address : type
        Descripción de connected_address.
    ack : bytes
    
        Descripción de ack. 
    seq : bytes
        Descripción de # secuencia.
    windows_length : int
        Descripción de windows_length.-
        
    """

    def __init__(self, sock=None):
        self.origin_address = None
        self.connected_address = None
        self.ack:bytes = None
        self.seq:bytes = None
        self.windows_length = 4

        self.time_init: float = None
        self.time_stop: float = None  # TODO:Definir el tiempo de parada
        self.time_mark: float = None
        self.time_estimated: float = 1
        self.time_desviation: float = 0
        self.time_interval: float = 1

        if sock == None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.socket = sock


    def start(self):
        now = time.time()
        self.time_mark = now
        if self.time_init == self.time_stop:
            self.time_init = now


    def running(self):
        return self.time_init != self.time_stop  # TODO: ????


    def timeout(self):
        if time.time() - self.time_init >= self.time_interval:
            self.time_interval *= 3 / 2
            self.time_init = self.time_stop
            # Aumentar la ventana de tiempo
            return True
        return False


    def waiter(self, time_wait):
        return self.running() and time.time() - self.time_mark >= time_wait


    def stop(self, retime = True):
        if retime:
            elapsed = time.time() - self.time_init
            self.time_estimated *= 7 / 8
            self.time_estimated += elapsed / 8

            self.time_desviation *= 3 / 4
            self.time_desviation += abs(elapsed - self.time_estimated) / 4

            self.time_interval = self.time_estimated + 4 * self.time_desviation
        self.time_init = self.time_stop


    def refresh(self, protocol):
        self.seq = get_bytes(protocol, 8, 12)
        self.ack = get_bytes(protocol, 4, 8) + 1


class ConnException(Exception):
    pass
# TODO: Implementar excepciones
