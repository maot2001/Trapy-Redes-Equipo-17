import datetime
import threading

class MyObject(object):
    def __init__(self):
        self.connections = {}  # Shared dictionary for connections
        self.lock = threading.RLock()  # Reentrant lock for safe access

    def add_connection(self, host, port):
        # Acquire the lock before modifying the dictionary
        with self.lock:
            # Obtener la hora actual
            connection_time = datetime.datetime.now()

            # Añadir la conexión al diccionario
            self.connections.update({(host, port): connection_time})
            
    def remove_connection(self, key):
    # Acquire the lock before modifying the dictionary
        with self.lock:
        # Comprobar si la conexión existe
            if key in self.connections.keys():
            # Eliminar la conexión del diccionario
                del self.connections[key]

"""""
# Create the object
object = MyObject()

# Create threads for adding, getting, and removing connection times
thread1 = threading.Thread(target=object.add_connection, args=("localhost", 6))
thread2 = threading.Thread(target=object.add_connection, args=("localhost", 9))
thread3 = threading.Thread(target=object.add_connection, args=("localhost", 80))
print ("jrthhjryl")
# Start the threads
thread1.start()
thread2.start()
thread3.start()

# Wait for all threads to finish
thread1.join()
thread2.join()
thread3.join()
auhjc=object.connections.keys()
# Print the connection time
keys_to_check = list(object.connections.keys())  # Crea una copia
for key in keys_to_check:
        last_connection = object.connections[key]
        now= datetime.datetime.now()
                    # If the connection has been dead for too long, close it.
        if (now.microsecond - last_connection.microsecond)> 1:
                        # Close the connection.
                         # Remove the connection from the list.
            object.remove_connection(key)
print ( "hola")
# Imprimir la hora de conexión
#print(connection_time)

"""""