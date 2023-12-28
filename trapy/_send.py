import threading
import time
from packet import *
from timer import Timer
from conn import *      
SLEEP_INTERVAL = 0.05
TIMEOUT_INTERVAL = 0.5
PACKET_SIZE = 512
END_CONN_INTERVAL = 5
end_conn_timer = False


base = 0
send_timer = Timer(TIMEOUT_INTERVAL)
mutex = threading.Lock()


def send(conn:Conn, data):
    global mutex
    global base
    global send_timer

    sock = conn.socket

    RECEIVER_ADDR = (conn.connected_address[0], conn.connected_address[1] )

    packets = create_pack_list(conn, data)
    num_packets = len(packets)
    window_size = set_window_size(num_packets)
    next_to_send = 0
    base = 0

    threading.Thread(target=receive, args=(sock,)).start()
    threading.Thread(target=countdown, args=(END_CONN_INTERVAL,)).start()

    while base < num_packets:
        
        mutex.acquire()
        while next_to_send < base + window_size:
            unpacked = my_unpack(packets[next_to_send])
            sock.sendto(packets[next_to_send], RECEIVER_ADDR)
            next_to_send += 1

        # Start the timer
        if not send_timer.running():
            # print('Starting timer')
            send_timer.start()

        # Wait until a timer goes off or we get an ACK
        while send_timer.running() and not send_timer.timeout():
            mutex.release()
            # print('Sleeping')
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()

        if send_timer.timeout():
            # Looks like we timed out
            # print('Timeout')
            send_timer.stop()
            next_to_send = base
        else:
            # print('Shifting window')
            window_size = set_window_size(num_packets)

        if end_conn_timer:
            mutex.release()
            raise Exception('WAITING TIME EXCEDED')
    
        mutex.release()

    print('last pack sent')

def countdown(t): 
    global mutex
    global send_timer
    global end_conn_timer

    while t > -1: 
        mutex.acquire()
        if not send_timer.running():
            mutex.release()
            return
        mutex.release()
        mins, secs = divmod(t, 60) 
        timer = '{:02d}:{:02d}'.format(mins, secs) 
        print(timer, end="\r") 
        time.sleep(1) 
        t -= 1
    mutex.acquire()
    send_timer.stop()
    end_conn_timer = True
    mutex.release()
    raise Exception('WAITING TIME EXCEDED')

WINDOW_SIZE = 4
def set_window_size(num_packets):
    global base
    return min(WINDOW_SIZE, num_packets - base)

def create_pack_list(conn, data):
    packets = []

    count = 1
    seq_num = conn.seq_num 
    ack = conn.ack
    while True:
        start = (count - 1)*PACKET_SIZE
        end = min(count*PACKET_SIZE, len(data))
        d = data[start:end]
        if end >= len(data):
            pack = create_last_send_packet(conn, seq_num, ack, d)
        else:
            pack = create_send_packet(conn, seq_num, ack, d)
        packets.append(pack)
        count += 1
        seq_num += 1
        ack += 1

        if end == len(data):
            break

    return packets

# Receive thread
def receive(sock):
    global mutex
    global base
    global send_timer
    while True:
        pkt, _ = recv(sock)
        ack_pack = my_unpack(pkt)
        # print('Received ack', ack_pack.ack)

        if (ack_pack.ack >= base):
            mutex.acquire()
            base = ack_pack.ack + 1
            # print('Base updated', base)
            send_timer.stop()
            mutex.release()
        
        if not send_timer.running():
            break

        mutex.acquire()
        if end_conn_timer:
            mutex.release()
            raise Exception('WAITING TIME EXCEDED')
        
# Receive a packet from the unreliable channel
def recv(sock):
    packet, addr = sock.recvfrom(1024)
    return packet, addr
    
