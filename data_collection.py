# This code was writen by Raafay Umar on 03-11-2023 from CIT

# project_folder
# │
# ├── data_collection.py
# │
# └── datafolder
#     │
#     ├── task
#         │
#         ├── sensors
#             │
#             ├── dates
#                 │
#                 └── data_files...


import socket
import threading
import os
import datetime
import json
import numpy as np


task = 'seat_belt'  # change accordingly, refer naming scheme dox.
sensor = 'ToF'  # change accordingly, refer naming scheme dox.
file_extension = 'npy'  # change accordingly.

load_previous = ''
arr = []

print(f'\nStart Data collection for Task: {task}\nand using the sensor: {sensor}\nFile extension: {file_extension}\n\nTo continue press Y, To change press N')
while True:
    choice = input('Y or N?\t').lower()
    if choice == 'y':
        break
    else:
        print('Please change the required values in the code and run the code again.')
        exit()

# Check if user_data.json exists
if os.path.exists('user_data.json'):
    load_previous = input('Do you want to load previous values? (yes/no): ')
    if load_previous.lower() == 'y':
        with open('user_data.json', 'r') as file:
            user_data = json.load(file)
    else:
        os.remove('user_data.json')
        user_data = None
else:
    user_data = None

# If user_data is None, ask for user input
if user_data is None:
    location = input('Enter location: la, co, cc, pa \n').lower()
    name = input('Name:  \n').lower()
    age = input('Age:  \n')
    gender = input('Gender:  \n').lower()
    contact_number = input('Enter contact number:  \n')
    spectacles = input('spectacles? wg, ng, sg:  \n').lower()
    run = int(input('Enter run number: 0x \n'))
    traffic = '0000-0000'

    # Save user data to user_data.json
    user_data = {
        'location': location,
        'name': name,
        'age': age,
        'gender': gender,
        'contact_number': contact_number,
        'spectacles': spectacles,
        'run': run,
        'traffic': traffic
    }
    with open('user_data.json', 'w') as file:
        json.dump(user_data, file)

#  Increment un number when loading previous initialization data
if user_data is not None and load_previous.lower() == 'y':
    user_data['run'] += 1
    with open('user_data.json', 'w') as file:
        json.dump(user_data, file)

UDP_IP = "0.0.0.0"
UDP_PORT = 12345  # port number of the sensor.
lux_values = 0

#  UDP setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)
current_path = os.getcwd()

# store the data in this directory
destination_dir = os.path.join(current_path, 'datafolder', task, sensor, '{}'.format(datetime.datetime.now().date()))

try:
    os.makedirs(destination_dir)
except OSError:
    pass


def receive_data():
    global lux_values
    while True:
        try:
            lux, _ = sock.recvfrom(1024)
            lux_values = lux.decode()
            lux_values = int(lux_values)
            print(lux_values)

        except socket.error:
            pass


# -------------------------------------------------------------------------------------- #
def user_function():
    frame_count = 0
    for i in range(0, 100):

        #  change the file ext.
        file_name = (f'{user_data["name"][:2]}_{user_data["contact_number"][-4:]}'
                     f'_{user_data["location"]}_{user_data["gender"]}_{user_data["age"]}'
                     f'_{user_data["spectacles"]}_{lux_values:04d}_{user_data["traffic"]}'
                     f'_{user_data["run"]:02d}_{frame_count:07d}.{file_extension}')

        # path to store data with filename.
        data = os.path.join(destination_dir, file_name)

        np.save(data, arr)
        frame_count += 1
    # add your code here...
# -------------------------------------------------------------------------------------- #


# Start a thread to receive data in the background
data_thread = threading.Thread(target=receive_data)
data_thread.daemon = True
data_thread.start()
user_function()
