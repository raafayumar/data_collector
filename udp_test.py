import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 9876

# UDP setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

while True:
    try:
        lux, _ = sock.recvfrom(1024)
        lux_values = int(lux.decode())
        print(lux_values)

    except socket.error:
        pass