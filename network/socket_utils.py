# network/socket_utils.py

import socket

def create_socket(host='localhost', port=8080):
    """Creates a socket and binds it to the specified host and port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    return s

def listen_for_connections(server_socket):
    """Listens for incoming connections on the provided server socket."""
    server_socket.listen(5)  # Allow up to 5 queued connections
    print(f"Listening for connections on {server_socket.getsockname()}...")
    return server_socket

def accept_connection(server_socket):
    """Accepts a new connection and returns the client socket and address."""
    client_socket, address = server_socket.accept()
    print(f"Connection accepted from {address}")
    return client_socket, address

def send_data(client_socket, data):
    """Sends data to the specified client socket."""
    client_socket.sendall(data.encode('utf-8'))
    print(f"Sent data: {data}")

def receive_data(client_socket, buffer_size=1024):
    """Receives data from the specified client socket."""
    data = client_socket.recv(buffer_size)
    print(f"Received data: {data.decode('utf-8')}")
    return data.decode('utf-8')

def close_socket(sock):
    """Closes the provided socket."""
    sock.close()
    print("Socket closed.")
