import socket
import time


class Conn:
    def __init__(self, sock=None):
        self.origin_address = None
        self.connected_address = None
        self.ack = None
        self.seq = None
        self.windows_length = 4

        self.time_init: float = None
        self.time_stop: float = None  # TODO:Definir el tiempo de parada
        self.time_mark: float = None
        self.time_estimated:float = 1
        self.time_desviatio:float = 0
        self.time_interval:float = 1

        if sock == None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.socket = sock

    def start(self):
        now = time.time()
        self.time_init = now
        self.time_mark = now

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


class ConnException(Exception):
    pass
# TODO: Implementar excepciones
