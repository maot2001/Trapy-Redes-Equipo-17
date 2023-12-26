
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
val=8
print(val.bit_length())
print(val.to_bytes((val.bit_length()), "big"))


f={"E":3,"jfjjf":9343434}

for value in f.keys():
    print(value)
    
# String
s = "Hola Mundo"

# Convertir el string a bytes utilizando la codificación UTF-8
b = s.encode('utf-8')

print(b)  # Imprime b'Hola Mundo'