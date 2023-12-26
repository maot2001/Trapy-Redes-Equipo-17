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

    def hand_shake_ACK(self):
        """
        Establece la conexión inicializando el atributo ACK a 1.

        Este método es parte del proceso de establecimiento de la conexión TCP,
        donde ACK es una abreviatura de "acknowledge". Al establecer ACK en 1,
        se indica que se está intentando iniciar una conexión.

        No toma ningún argumento y no devuelve ningún valor.
        """
        self.SYN=1
        self.ACK = 1
    def close_connection(self):
        """
        Cierra la conexión inicializando el atributo FIN a 1.

        Este método es parte del proceso de cierre de la conexión TCP,
        donde FIN es una abreviatura de "finish". Al establecer FIN en 1,
        se indica que se está intentando cerrar la conexión.

        No toma ningún argumento y no devuelve ningún valor.
        """
        self.FIN = 1
        
    def from_bytes_to_flags(self,flags_bytes):
        flags = [(128,"cwr"), (64,"ece"), (32,"urg"), (16,"ack"), (8,"las"), (4,"rst"), (2,"syn"), (1,"fin")]
    
        num = int.from_bytes(flags_bytes, "big") if isinstance(flags_bytes, bytes) else flags_bytes
        for bit, flag in flags:
            if num & bit:
                on_flags.add(flag)
        
        