import socket

class Conn:
    """
    Esta es la clase Conn. Aquí puedes describir la clase.

    Atributos
    ---------
    origin_address : type
       Address origen.
    connected_address : type
       Address Destino.
    ack : bytes
    
        Descripción de ack. 
    seq : bytes
        Descripción de # secuencia.
    windows_length : int
        Descripción de windows_length.-
        
    """

    def __init__(self, sock=None):
        self.origin_address: tuple[str, int] = None
        self.connected_address: list(tuple[str, int]) = []

        self.ack: list(bytes) = []
        self.seq: list(bytes) = []
        
        self.windows_length = 4
        #self.buffer = ()

        """self.time_init: float = None
        self.time_stop: float = None  # TODO:Definir el tiempo de parada
        self.time_mark: float = None
        self.time_estimated: float = 1
        self.time_desviation: float = 0
        self.time_interval: float = 1"""

        if sock == None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.socket = sock

    """def start(self):
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
        self.time_init = self.time_stop"""

    def refresh(self, index, new_ack, new_seq, data):
        self.seq[index] = new_ack
        self.ack[index] = new_seq + data

class ConnException(Exception):
    pass