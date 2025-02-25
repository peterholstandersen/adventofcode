import socket
import sys

host = "localhost"
port = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

while True:
    message = input()
    print("sending input:", message)
    sock.sendall(str.encode(message))
