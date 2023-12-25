import socket
"""
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

ip_header  = b'\x45\x00\x00\x28'  # Version, IHL, Type of Service | Total Length
ip_header += b'\xab\xcd\x00\x00'  # Identification | Flags, Fragment Offset
ip_header += b'\x40\x06\xa6\xec'  # TTL, Protocol | Header Checksum
ip_header += b'\x0a\x00\x00\x01'  # Source Address
ip_header += b'\x0a\x00\x00\x02'  # Destination Address

tcp_header  = b'\x30\x39\x00\x50' # Source Port | Destination Port
tcp_header += b'\x00\x00\x00\x00' # Sequence Number
tcp_header += b'\x00\x00\x00\x00' # Acknowledgement Number
tcp_header += b'\x50\x02\x71\x10' # Data Offset, Reserved, Flags | Window Size
tcp_header += b'\xe6\x32\x00\x00' # Checksum | Urgent Pointer

packet = ip_header + tcp_header
s.sendto(packet, ('127.0.0.1', 8000))
print('Send Packet')


s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

s.bind(('127.0.0.1', 8000))
print('bind successful')

while True:
    print(s.recvfrom(65565))
"""
"""
import socket

# Crear un socket
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

# Establecer la opción IP_HDRINCL
s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# Vincular el socket a una dirección y puerto
s.bind(('127.0.0.1', 8000))
print('bind successful')

# Crear un paquete para enviar
packet = b'Hello, world!'

# Enviar el paquete a la misma dirección y puerto
s.sendto(packet, ('127.0.0.1', 8000))

while True:
    # Recibir cualquier paquete entrante
    data, addr = s.recvfrom(65565)
    print('Received from:', addr)
    print('Received data:', data)
    """
import socket

    # Crear un socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Vincular el socket a una dirección y puerto
s.bind(('127.0.0.1', 8000))
print('bind successful')
# Escuchar conexiones entrantes
s.listen(1)
print('listening for connections')
# Aceptar una conexión entrante
conn, addr = s.accept()
print('connected by', addr)
# Crear un mensaje para enviar
message = b'Viva la libertad carajo!'
# Enviar el mensaje
conn.sendall(message)
while True:
    # Recibir cualquier mensaje entrante
    data = conn.recv(1024)
    if not data:
        break
    print('Received data:', data)
# Cerrar la conexión
conn.close()