import socket
import threading
import traceback
import sys
from time import sleep

rlock = threading.RLock(blocking=True, timeout=-1)

class ClientConnection(threading.Thread):
    # From the client's perspective the socket is the server_socket
    def __init__(self, server_socket, address):
        threading.Thread.__init__(self)
        self.server_socket = server_socket
        self.address = address

    def debug(self, text):
        print(f"Client {self.address[1]}: {text}")
        # print(f"Client {threading.get_ident()}: {text}")

    def run(self):
        global x
        debug = self.debug
        debug("client thread started")
        while True:
            try:
                debug("waiting for input")
                data = self.server_socket.recv(32)
                if len(data) == 0:
                    debug("server dropped connection")
                    break
                debug(f"received {len(data)} bytes: {str(data.decode('utf-8'))}")
            except Exception as e:
                traceback.print_exc()
                debug("continue client thread")
        debug("closing client thread")

def accept_connections(server_socket):
    # running in the main thread, i.e., the server thread
    while True:
        print("Server: waiting for connections")
        client_socket, address = server_socket.accept()
        print("Server: accepted connection")
        client_connection = ClientConnection(client_socket, address)
        client_thread = threading.Thread(target = client_connection.run)
        # threading.excepthook: https://docs.python.org/3/library/threading.html
        client_thread.start()

def main():
    host = "localhost"
    port = 5000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    accept_connections(server_socket)

if __name__ == "__main__":
    main()
