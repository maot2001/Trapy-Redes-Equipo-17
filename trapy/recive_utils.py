from scapy.all import IP, TCP,Raw,raw

#def join_byte_arrays(byte_arrays):
 #   return b''.join(byte_arrays)


def join_byte_arrays(byte_arrays):
    # Aplanar la lista de listas en una sola lista
    flattened = [item for sublist in byte_arrays for item in sublist]
    
    # Unir todos los arrays de bytes en uno solo
    return b''.join(flattened)

def generate_new_seq_number(current_seq_number, data):
    # Calcular la longitud de los datos en bytes
    data_length = len(data)
    
    # Sumar la longitud de los datos al número de secuencia actual
    new_seq_number = current_seq_number + data_length
    
    return new_seq_number



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

def build_packet_with_data(src_ip, dst_ip, src_port, dst_port, flags, data):
    # Crear el paquete IP
    ip_header = IP(src=src_ip, dst=dst_ip)
    
    # Crear el paquete TCP
    tcp_header = TCP(sport=src_port, dport=dst_port, flags=flags)
    
    # Añadir los datos al paquete
    packet = ip_header / tcp_header / Raw(load=data)
    
    return packet


def generate_new_seq_number(packet):
    # Obtener el número de secuencia actual y los datos del paquete
    current_seq_number = packet[TCP].seq
    data = packet[TCP].payload

    # Calcular la longitud de los datos en bytes
    data_length = len(data)

    # Sumar la longitud de los datos al número de secuencia actual
    new_seq_number = current_seq_number + data_length

    return new_seq_number


def extract_data(packet)->bytes:
    # Comprobar si el paquete tiene datos (payload)
    if Raw in packet:
        # Extraer los datos en bytes
        data = packet[Raw].load
        return data
    else:
        return None

"""
# Ejemplo de uso
data, _= conn.socket.recvfrom(mss)
packet = IP(data)
new_seq_number = generate_new_seq_number(packet)

# Ejemplo de uso
data = b'Hello, world!'
packet = build_packet_with_data('192.168.1.1', '192.168.1.2', 12345, 80, 'S', data)

# Recibir un paquete
data, _ = conn.socket.recvfrom(mss)

# Analizar el paquete con Scapy
packet = IP(data)

# Obtener la información del paquete
src_ip = packet[IP].src
dst_ip = packet[IP].dst
src_port = packet[TCP].sport
dst_port = packet[TCP].dport
flags = packet[TCP].flags
seq_num = packet[TCP].seq
ack_num = packet[TCP].ack
payload_data = packet[TCP].payload

print(f"Source IP: {src_ip}")
print(f"Destination IP: {dst_ip}")
print(f"Source port: {src_port}")
print(f"Destination port: {dst_port}")
print(f"Flags: {flags}")
print(f"Sequence number: {seq_num}")
print(f"Acknowledgement number: {ack_num}")
print(f"Payload data: {payload_data}")
"""