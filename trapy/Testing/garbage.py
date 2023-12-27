def get_address_from_bytes_to_str(address:bytes) -> str:
   
        return ".".join(str(byte) for byte in address)    


def get_property_from_bytes_to_int(data:bytes):
             
        return int.from_bytes(data, "big")
    
    
def str_to_bytes(value:str)->bytes:
   return value.encode('utf-8')

a="127.0.0.1"
a_b=str_to_bytes(a)
print(a_b)


def str_to_32_bytes(value:str) -> bytes:
    return value.ljust(4).encode('utf-8')

a = "127.0.0.1"
a_b = str_to_32_bytes(a)
print(a_b)
print(get_address_from_bytes_to_str(a_b))
import socket

def ip_str_to_bytes(ip_str: str) -> bytes:
    return socket.inet_aton(ip_str)

# Ejemplo de uso
ip_str = "127.0.0.1"
ip_bytes = ip_str_to_bytes(ip_str)
print(ip_bytes)  # Imprime: b'\x7f\x00\x00\x01'


def bytes_to_ip_str(address: bytes) -> str:
    return socket.inet_ntoa(address)

# Ejemplo de uso
#ip_bytes = b'\x7f\x00\x00\x01'  # 127.0.0.1 en bytes
ip_str = bytes_to_ip_str(ip_bytes)
print(ip_str)  # Imprime: 127.0.0.1






def bytes_to_int(b:bytes):
    return int.from_bytes(b, "big")


def int_to_bytes(number, size:int)->bytes:
    """
    Converts an integer to a byte array of specified size.

    Args:
        number (int): The integer to convert.
        size (int): The size of the resulting byte array.

    Returns:
        bytes: The byte array representation of the integer.
    """
    return number.to_bytes((size), "big")



a=1234

a_b=int_to_bytes(a,32)

print(bytes_to_int(a_b))

