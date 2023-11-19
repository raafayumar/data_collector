""" This code was created by Raafay Umar on 03-11-2023 from CIT

1. Folder Structure:
   Ensure your project follows the following structure:
     project_folder
     │
     ├── initializer.py
     │
     └── your_code.py
     │
     └── configs
     │
     └── datafolder
         │
         ├── task
             │
             ├── sensors
                 │
                 ├── dates
                     │
                     └── data_files...

2. Import the Module:
   Ensure that the 'initializer.py' module is in the same directory as your Python script.

   Example:
   from initializer import initialize_details, getLux, file_constructor

3. Initializing Task and Sensor Information:
   Call the `initialize_details` function to set up task and sensor details.
   This function will prompt for user input if no previous details are available.

   Example:
   task_info, user_configuration = initialize_details()

   - `task_info`: Dictionary containing task and sensor information.
   - `user_configuration`: Dictionary containing subject details.

5. Constructing File Names:
   Use the `file_constructor` function to construct file names based on user information and lux values.

   Example:
    path = file_constructor()
    file_name = f'{path}_{frame_count:07d}.{file_extension}'
    data = os.path.join(path, file_name)

   This naming convention includes information about the user, sensor, and lux values.

   Note: call this in a loop.
         increment frame_count after saving each frame.
         assign proper file_extension.


"""

import socket
import os
import datetime
import json
import threading


load_previous = ''
task_choice = ''

lux_values = 0

current_path = os.getcwd()
os.makedirs(os.path.join(current_path, 'configs'), exist_ok=True)

task_and_sensor_file = os.path.join('configs', 'task_config.json')
details_file = os.path.join('configs', 'details_config.json')
user_configuration = {}
destination_dir = ''


def getLux():
    global lux_values, destination_dir
    UDP_IP = "0.0.0.0"
    UDP_PORT = 12345

    #  UDP setup
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)

    while True:
        try:
            lux, _ = sock.recvfrom(1024)
            lux_values = lux.decode()
            lux_values = int(lux_values)

        except socket.error:
            # print('No Data received from sensor.')
            pass


data_thread = threading.Thread(target=getLux)
data_thread.daemon = True
data_thread.start()


def initialize_details():
    global load_previous, task_choice, destination_dir, user_configuration

    #  Task and Sensor Initialization.
    if os.path.exists(task_and_sensor_file):
        with open(task_and_sensor_file, 'r')as f1:
            task_and_sensor_info = json.load(f1)

            print(f'\nStart Data collection for Task: {task_and_sensor_info["task"]}\n'
                  f'and using the sensor: {task_and_sensor_info["sensor"]}\n\n'
                  f'To continue press Y, To change press N')

            task_choice = input().lower()
            f1.close()

            if task_choice.lower() == 'y':
                with open(task_and_sensor_file, 'r') as file_1:
                    task_and_sensor_info = json.load(file_1)
            else:
                os.remove(task_and_sensor_file)
                task_and_sensor_info = None
    else:
        task_and_sensor_info = None

    #  Create a json file for task and sensor.
    if task_and_sensor_info is None:
        task = input('Enter Task name:\n').lower()
        sensor = input('Enter Sensor:\n').lower()

        task_and_sensor_info = {
            'task': task,
            'sensor': sensor
        }
        with open(task_and_sensor_file, 'w') as file_1:
            json.dump(task_and_sensor_info, file_1)

    # Check if details_file exists
    if os.path.exists(details_file):
        with open(details_file) as file:
            user_configuration = json.load(file)

            print(f'\n\nSubject name: {user_configuration["name"]}\n'
                  f'Spectacles: {user_configuration["spectacles"]}\n')

            load_previous = input('Do you want to load previous initialization details mentioned above? (yes/no):\n')
            file.close()

        if load_previous.lower() == 'y':
            with open(details_file, 'r') as file:
                user_configuration = json.load(file)
        else:
            os.remove(details_file)
            user_configuration = None
    else:
        user_configuration = None

    # If user_configuration is None, ask for user input
    if user_configuration is None:
        location = input('Enter location: la, co, cc, pa \n').lower()
        name = input('Name:  \n').lower()
        age = input('Age:  \n')
        gender = input('Gender:  \n').lower()
        contact_number = input('Enter contact number:  \n')
        spectacles = input('spectacles? wg, ng, sg:  \n').lower()
        run = int(input('Enter run number: 0x \n'))
        traffic = '0000-0000'

        # Save user data to details_file
        user_configuration = {
            'location': location,
            'name': name,
            'age': age,
            'gender': gender,
            'contact_number': contact_number,
            'spectacles': spectacles,
            'run': run,
            'traffic': traffic
        }
        with open(details_file, 'w') as file:
            json.dump(user_configuration, file)

    #  Increment run number when loading previous initialization data
    if user_configuration is not None and load_previous.lower() == 'y':
        user_configuration['run'] += 1
        with open(details_file, 'w') as file:
            json.dump(user_configuration, file)

    # store the data in this directory
    destination_dir = os.path.join(current_path, 'datafolder', task_and_sensor_info["task"],
                                   task_and_sensor_info["sensor"],
                                   '{}'.format(datetime.datetime.now().date()))

    try:
        os.makedirs(destination_dir)
    except OSError:
        pass

    return task_and_sensor_info, user_configuration


def file_constructor():
    # Construct file name using user information and lux value
    file_name = (f'{user_configuration["name"][:2]}_{user_configuration["contact_number"][-4:]}'
                 f'_{user_configuration["location"]}_{user_configuration["gender"]}_{user_configuration["age"]}'
                 f'_{user_configuration["spectacles"]}_{lux_values:04d}_{user_configuration["traffic"]}'
                 f'_{user_configuration["run"]:02d}')

    data = os.path.join(destination_dir, file_name)

    return data
