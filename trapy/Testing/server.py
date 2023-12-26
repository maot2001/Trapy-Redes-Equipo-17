import sys, getopt
import sys
sys.path.append("/home/Codes/redes/Trapy-Redes-Equipo-17/trapy")




from trapy import listen, accept, send, recv, close
#from socket_trapy import *

host = "10.0.0.1"
#host = "0.0.0.0"
port = 6

print("-------------SERVER---------------")
print("Listening on:", host, ":", port)
server = listen(host + f":{port}")
print("Conexion por aceptar")
server_1 = accept(server)
print('Conexion aceptada')
c = 0
print('Tenemos el server')
while server_1 != None and c < 5:
    print('A enviar')
    print('valor de c:',c)
    r = recv(server_1, 20)
    print("*******Data Recieved*******\n", r)
    a = send(server_1, r)
    print("*******Data Sent***********\n", r[0:a])
    print("----------Succeded-----------")
    c += 1
    input()
else:
    close(server_1)
close(server)
print('Close Server')

