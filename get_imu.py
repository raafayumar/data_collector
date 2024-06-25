import socket
import csv
import time

UDP_IP = "0.0.0.0"
UDP_PORT = 2828

# Field names for CSV headers
headers = [
    "accx", "accy", "accz", "gyrx", "gyry", "gyrz", "qw", "qx", "qy", "qz", "qyaw", "qpitch", "qroll",
    "yaw", "pitch", "roll", "gravaccx", "gravaccy", "gravaccz", "counter"
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
        data, _ = sock.recvfrom(1024)
        data_values = data.decode().split(',')
        print(data_values)

        # Make sure the received data has all the required fields
        if len(data_values) == len(headers):
            timestamp = time.time()  # Get current timestamp
            data_values.append(str(timestamp))  # Append timestamp at the end

            with open(path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(data_values)
        else:
            print("Received incomplete data. Skipping.")
    except socket.error:
        pass
