import socket
#IP Protocol IPv4
#Raw Socket (Socket crudo)
#El programa maneja el socket manualmente
s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
#IP Protocol
#Manejar el encabezado IP manualmente
s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
# Vincular en la red IP privada 10.0.0.2
#Puerto a elegir pot el SO que este libte

<<<<<<< HEAD
s.bind(('10.0.0.2', 0))
#Recibir paquetes
#tamaño maximo de 65565 bytes
#Devuelve una tupla con el paquete y la direccion de origen
=======
s.bind(('127.0.0.1', 8000))

>>>>>>> b03c0ab (Testing)
while True:
    print(s.recvfrom(8000))
