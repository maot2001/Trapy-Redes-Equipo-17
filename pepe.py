def join_byte_arrays(byte_arrays):
    return b''.join(byte_arrays)

# Ejemplo de uso
byte_arrays = [b'Hello, ', b'world!']
joined_bytes = join_byte_arrays(byte_arrays)
print(joined_bytes)  # Imprime: b'Hello, world!'b"\x50"
print(b"\x50")


print(b"hola")
print(b'mundo')

print(b'holamundo')

s = "Holamundkkkk"
binary = ' '.join(format(ord(c), '08b') for c in s)
print(binary)

data = b'10'

print(len(data))  # Imprime: 

from scapy.all import IP, raw

def is_packet_corrupt(packet):
    # Guardar el checksum original y establecer el campo de checksum del paquete a 0
    original_checksum = packet.chksum
    packet.chksum = 0

    # Calcular el checksum esperado
    expected_checksum = IP(raw(packet)).chksum

    # Restaurar el checksum original en el paquete
    packet.chksum = original_checksum

    # Comprobar si el checksum original coincide con el esperado
    return original_checksum != expected_checksum

# Ejemplo de uso
ip_packet = IP(src="192.168.1.1", dst="192.168.1.2")
print(is_packet_corrupt(ip_packet))





def join_byte_arrays(byte_arrays):
    return b''.join(byte_arrays)

# Ejemplo de uso
arr1=[b'Hello,']
arr2=[b'world!']
byte_arrays = [ arr1,arr2]
#joined_bytes = join_byte_arrays(byte_arrays)
#print(joined_bytes)  # Imprime: b'Hello, world!'

def join_byte_arrays(byte_arrays):
    # Aplanar la lista de listas en una sola lista
    flattened = [item for sublist in byte_arrays for item in sublist]
    
    # Unir todos los arrays de bytes en uno solo
    return b''.join(flattened)

# Ejemplo de uso
arr1 = [b'Hello,']
arr2 = [b'world!']
byte_arrays = [arr1, arr2]
joined_bytes = join_byte_arrays(byte_arrays)
print(joined_bytes)  # Imprime: b'Hello,world!'


a:int=4
a="j"