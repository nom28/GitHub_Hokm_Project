from socket import *
import os

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 55557  # The port used by the server

with socket(AF_INET, SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while(True):
        data = s.recv(1024)
        print(data)
