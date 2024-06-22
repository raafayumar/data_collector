import socket
import csv
import time

UDP_IP = "0.0.0.0"
UDP_PORT = 2828

# Field names for CSV headers
headers = [
    "timestamp", "counter", "accx", "accy", "accz", "gyrx", "gyry", "gyrz", "qx", "qy", "qz", "qyaw", "qpitch", "qroll",
    "yaw", "pitch", "roll", "gravaccx", "gravaccy", "gravaccz"
]

# UDP setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)


def create_csv(path):
    # Create a new CSV file with headers
    with open(path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)


def imu_data(path):
    try:
        lux, _ = sock.recvfrom(1024)
        lux_values = lux.decode().split(',')
        print(lux_values)
        # Make sure the received data has all the required fields
        if len(lux_values) == len(headers) - 4:  # Excluding timestamp and flags from the count
            timestamp = time.time()  # Get current timestamp
            lux_values.insert(0, str(timestamp))  # Insert timestamp at the beginning

            with open(path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(lux_values)
        else:
            print("Received incomplete data. Skipping.")
    except socket.error:
        pass
