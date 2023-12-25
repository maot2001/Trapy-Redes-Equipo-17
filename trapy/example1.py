import socket

# Crear un socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conectarse a la dirección y puerto
s.connect(('127.0.0.1', 8000))
print('connection successful')

# Recibir cualquier mensaje entrante
data = s.recv(1024)
print('Received data:', data)

# Cerrar la conexión
#
s.close()