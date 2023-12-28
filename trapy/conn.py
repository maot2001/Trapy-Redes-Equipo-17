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

        """
        Aqui van los datos de todas la conexiones q estan establecidas con el origin_address
        
        Se debe acceder a los datos de cada una por el indice asociado al connected_address, con este se puede saber los valores
        de ack y seq, con nombre.connected_address.index(address) tienen ese indice, address deben recibirlo de data_conn luego
        de separar la info del paquete recibido
        
        Para comprobar la existencia de address en connected_address pueden usar: if address in connected_address y asi evitar
        errores de mensajes

        No me queda claro que el proyecto necesite estas listas de conexiones, creo que las conexiones de un origen con varios
        destinos podria representarse como varios conn, pero para el send y recv no se que les sera mas comodo

        En accept hice un comentario sobre el tipado de self.ack y sel.seq
        """
        self.connected_address: list(tuple[str, int]) = []
        self.ack: list(bytes) = []
        self.seq: list(bytes) = []
        
        self.windows_length = 4

        if sock == None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.socket = sock

    def refresh(self, index: int, new_ack: int, new_seq: int, data: int):
        """
        Este metodo les permite modificar los ack y seq pasando el tamaño del paquete recibido, ahora mismo todos los valores
        son int, pero puede hacerse con bytes o con lo que sea, la idea no cambia
        """
        self.seq[index] = new_ack.to_bytes(4,byteorder='big', signed=False)
        new_seq += data
        self.ack[index] = new_seq.to_bytes(4,byteorder='big', signed=False)


    

class ConnException(Exception):
    pass