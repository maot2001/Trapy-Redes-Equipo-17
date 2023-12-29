import threading
import time
import datetime
from rwlock import MyObject
class TimeoutChecker(threading.Thread):

    def __init__(self, object:MyObject, timeout):
        super().__init__(daemon=True)
        self.object = object
        self.timeout = timeout

    def run(self):
        while True:
            print("daemon")
            # Obtener el tiempo actual
            now = datetime.datetime.now()

            # Iterar sobre las conexiones
            keys_to_check = list(object.connections.keys())  # Crea una copia
            for key in keys_to_check:
                last_connection = object.connections[key]
                now= datetime.datetime.now()
                    # If the connection has been dead for too long, close it.
                if (now.microsecond - last_connection.microsecond)> 1:
                    self.object.remove_connection(key)
            # Dormir durante el tiempo de espera
            time.sleep(self.timeout)

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

# Crear un hilo demonio para revisar el diccionario
checker = TimeoutChecker(object, 1)
checker.start()

    # Esperar a que el hilo demonio haya terminado
time.sleep(2)

    # Comprobar que la conexión ha sido eliminada
assert object.connections == {}
"""""