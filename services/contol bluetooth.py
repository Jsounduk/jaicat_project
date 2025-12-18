import socket

# Define a function to connect to a Bluetooth device
def connect_to_bluetooth_device(device_address, port):
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect((device_address, port))
    return s

# Define a function to send a command to a Bluetooth device
def send_command_to_bluetooth_device(s, command):
    s.send(command.encode())
    response = s.recv(1024)
    return response.decode()

# Define a function to control a sexual Bluetooth device
def control_sexual_bluetooth_device(device_address, port, command):
    s = connect_to_bluetooth_device(device_address, port)
    response = send_command_to_bluetooth_device(s, command)
    print(f"Response from device: {response}")
    s.close()

# Example usage:
device_address = "B8:27:EB:22:57:E0"
port = 1
command = "vibrate"
control_sexual_bluetooth_device(device_address, port, command)
