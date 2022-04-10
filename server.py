import os
import socket

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SAVE_PATH = "./remote-logs"

s = socket.socket()
s.bind((SERVER_HOST, SERVER_PORT))
s.listen(5)
print(f"[~] Listening as {SERVER_HOST} : {SERVER_PORT}")

if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

client_socket, client_address = s.accept()
print(f"[~] {client_address} is connected!")

while True:
    filename = client_socket.recv(BUFFER_SIZE).decode()
    bytes_received = client_socket.recv(BUFFER_SIZE)
    with open(os.path.join(SAVE_PATH, filename), 'wb') as f:
        f.write(bytes_received)
    print(f"[+] Received {SAVE_PATH}/{filename}.txt")
    
client_socket.close()
s.close()
