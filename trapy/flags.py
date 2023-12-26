from enum import Enum

class Flags:
    def __init__(self):
        self.ACK = 0
        self.SYN = 0
        self.FIN = 0
  
    
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