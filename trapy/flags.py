from enum import Enum

class Flags:
    def __init__(self, flag: bytes = 0):
        bits = self.obtener_bits(flag)
        self.CWR = bits[7]
        self.ECE = bits[6]
        self.URG = bits[5]
        self.ACK = bits[4]
        self.PSH = bits[3]
        self.RST = bits[2]
        self.SYN = bits[1]
        self.FIN = bits[0]
    
    def obtener_bits(self, byte):
        bits = []
        for i in range(8):
            bit = (byte >> i) & 1
            bits.append(bit)
        return bits
    
def make_connection(self):
    """
    Establece la conexión inicializando el atributo SYN a 1.

    Este método es parte del proceso de establecimiento de la conexión TCP,
    donde SYN es una abreviatura de "synchronize". Al establecer SYN en 1,
    se indica que se está intentando iniciar una conexión.

    No toma ningún argumento y no devuelve ningún valor.
    """
    self.SYN = 1


def close_connection(self):
    """
    Cierra la conexión inicializando el atributo FIN a 1.

    Este método es parte del proceso de cierre de la conexión TCP,
    donde FIN es una abreviatura de "finish". Al establecer FIN en 1,
    se indica que se está intentando cerrar la conexión.

    No toma ningún argumento y no devuelve ningún valor.
    """
    self.FIN = 1