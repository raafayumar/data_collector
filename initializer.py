""" This code was created by Raafay Umar on 19-11-2023.

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

2. 1. Import the Module:
   Ensure that the 'initializer.py' module is in the same directory as your Python script.

   Example:
   from initializer import initialize_details, file_constructor

2. Initializing Task and Sensor Information:
   Call the `initialize_details` function to set up task and sensor details.
   This function will prompt for user input if no previous details are available.

   Example:
   data_dir = initialize_details('your_sensor_name')
   - `data_dir`: Path to the directory where data will be stored.

3. Constructing File Names:
   Use the `file_constructor` function to construct file names based on user information and lux values.
   this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”

   Example:
   file_name = file_constructor()
   - `file_name`: The constructed file name including information about the user, sensor, and lux values.

   Note: Call `file_constructor` in a loop.
         Increment frame_count after saving each frame.
         Assign a proper file_extension.


"""

import socket
import os
import datetime
import json
import threading
import time
import cv2
import tkinter as tk
from tkinter import simpledialog
import csv
import sys


load_previous = ''
task_choice = ''
lux_values = 0


def get_working_directory():
    if getattr(sys, 'frozen', False):
        # If the application is frozen, use this path
        current_path = os.path.dirname(sys.executable)
    else:
        # If not frozen, use this path
        current_path = os.path.dirname(os.path.realpath(__file__))
    return current_path


current_path = get_working_directory()
os.makedirs(os.path.join(current_path, 'configs'), exist_ok=True)


class ImageAnnotator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Annotator")

        # Withdraw the window to avoid blocking
        self.root.withdraw()

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack()

        self.class_names = None
        self.current_class = None
        self.bbox = None

        self.is_capturing = False
        self.frame = None
        self.annotation_string = ''

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def set_class_names(self, class_names):
        self.class_names = class_names

    def annotate_frame(self, frame):
        self.frame = frame
        self.annotate_frame_internal()

    def annotate_frame_internal(self):
        # Resize the frame to fit within a certain size
        max_width = 800  # Maximum width of the displayed image
        max_height = 600  # Maximum height of the displayed image
        try:
            height, width, _ = self.frame.shape
            if width > max_width or height > max_height:
                if width / max_width > height / max_height:
                    ratio = max_width / width
                else:
                    ratio = max_height / height
                self.frame = cv2.resize(self.frame, (int(width * ratio), int(height * ratio)))
        except:
            pass

        self.bbox = cv2.selectROI('Annotation', self.frame, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow('Annotation')
        self.get_class_input()

    def get_class_input(self):
        choices = "\n".join([f'Enter {i} for {class_name}' for i, class_name in enumerate(self.class_names)])
        self.current_class = simpledialog.askstring('Class', choices)
        self.annotation_string = self.get_annotation_string()
        self.root.destroy()  # Close the Tkinter window after annotating

    def get_annotation_string(self):
        class_label = self.current_class
        x, y, w, h = self.bbox
        cx = (x + w / 2) / self.frame.shape[1]
        cy = (y + h / 2) / self.frame.shape[0]
        bw = w / self.frame.shape[1]
        bh = h / self.frame.shape[0]
        return f'{class_label} {cx} {cy} {bw} {bh}'

    def on_canvas_click(self, event):
        if not self.is_capturing:
            self.annotate_frame_internal()


def getLux():
    global lux_values
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

        except socket.error:
            pass


data_thread = threading.Thread(target=getLux)
data_thread.daemon = True
data_thread.start()


def send_trigger():
    # ESP32 IP address and port
    esp_ip = "192.168.0.4"  # Replace with the IP address of your ESP32
    esp_port = 2828
    esp_msg = '1'
    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for i in range(2):
        # Send the message
        sock.sendto(esp_msg.encode(), (esp_ip, esp_port))


def initialize_details(sensor_name=None):
    global load_previous, task_choice, user_configuration, task_and_sensor_info

    # Check if the sensor_name is provided and in the predefined list
    sensor_list = ['azure_ir', 'azure_depth', 'azure_rgb', 'ti_radar', 'vayyar_radar', 'thermal', 'tof_ir', 'tof_depth',
                   'intel_depth', 'intel_rgb']
    task_list = ['seat_belt', 'hands_on_off_steering', 'gaze_detection', 'driver_face', 'driver_pose', 'driver_vitals',
                 'occupant_vitals', 'gesture_recognition', 'occupant', 'breathing']

    if sensor_name is None or sensor_name not in sensor_list:
        print("Invalid sensor name. Choose from the following options:\n")
        for item in sensor_list:
            print(item)
        exit()

    # Task and Sensor Initialization.
    task_and_sensor_file = os.path.join('configs', f'{sensor_name}_config.json')

    if os.path.exists(task_and_sensor_file):
        with open(task_and_sensor_file, 'r') as f1:
            task_and_sensor_info = json.load(f1)

            print(f'\nStart Data collection for Task: {task_and_sensor_info["task"]}\n'
                  f'and using the sensor: {task_and_sensor_info["sensor"]}\n\n'
                  f'To continue press Y, To change press N')

            task_choice = input().lower()

            if task_choice.lower() == 'y':
                with open(task_and_sensor_file, 'r') as file_1:
                    task_and_sensor_info = json.load(file_1)

            else:
                f1.close()
                os.remove(task_and_sensor_file)
                task_and_sensor_info = None
    else:
        task_and_sensor_info = None

    # Create a json file for task and sensor.
    if task_and_sensor_info is None:
        task = input(f'Enter Task name for {sensor_name}:\n').lower()

        if task not in task_list:
            print("Invalid task entered. Please choose from the following options:\n")
            for items in task_list:
                print(items)
            exit()

        task_and_sensor_info = {
            'task': task,
            'sensor': sensor_name
        }
        with open(task_and_sensor_file, 'w') as file_1:
            json.dump(task_and_sensor_info, file_1)

    # Check if details_file exists
    details_file = os.path.join('configs', f'{sensor_name}_details_config.json')
    if os.path.exists(details_file):
        with open(details_file) as file:
            user_configuration = json.load(file)

            print(f'\n\nSubject name: {user_configuration["name"]}\n'
                  f'Spectacles: {user_configuration["spectacles"]}\n')

            load_previous = input('Do you want to load previous initialization details mentioned above? (y/n):\n')

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
        if location not in ['la', 'co', 'cc', 'pa']:
            print(f'Please enter the correct location details\n')
            location = input('Enter location: la, co, cc, pa \n').lower()

        name = input('Name:  \n').lower()

        age = input('Age:  \n')
        if not age.isnumeric():
            print('Please enter valid age\n')
            age = input('Age:  \n')

        gender = input('Gender:  \n').lower()
        if len(gender) > 1:
            gender = gender[0]

        contact_number = input('Enter contact number:  \n')
        if len(contact_number) < 10 and contact_number.isnumeric():
            print('Please enter correct contact number\n')
            contact_number = input('Enter contact number:  \n')

        spectacles = input('spectacles? wg, ng, sg:  \n').lower()
        if spectacles not in ['wg', 'sg', 'ng']:
            print('Please enter correct details\n')
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

    # Increment run number when loading previous initialization data
    if user_configuration is not None and load_previous.lower() == 'y':
        user_configuration['run'] += 1
        with open(details_file, 'w') as file:
            json.dump(user_configuration, file)
    # Store the data in this directory
    destination_dir = os.path.join(current_path, 'datafolder', task_and_sensor_info["task"],
                                   task_and_sensor_info["sensor"],
                                   '{}'.format(datetime.datetime.now().date()))

    try:
        os.makedirs(destination_dir)
    except OSError:
        pass

    return destination_dir


def file_constructor(conditions, classes):
    t = str(time.time())
    time_stamp = t.replace('.', '-')
    # Construct file name using user information and lux value
    file_name = (f'{time_stamp}_{user_configuration["name"][:2]}_{user_configuration["contact_number"][-4:]}'
                 f'_{user_configuration["location"]}_{user_configuration["gender"]}_{user_configuration["age"]}'
                 f'_{user_configuration["spectacles"]}_{lux_values:05d}_{conditions:04d}-{classes:04d}'
                 f'_{user_configuration["run"]:02d}')

    return file_name


def add_comments_all(task, sensor, content, fps, toc, classes, road_condition, traffic_condition, electronic_disturbance):
    t = str(time.time())
    t_stamp = t.replace('.', '-')
    meta_file = 'metadata_v1.csv'
    meta_path = os.path.join(current_path, 'metadata')
    os.makedirs(meta_path, exist_ok=True)

    if not os.path.exists(os.path.join(meta_path, meta_file)):
        with open(os.path.join(meta_path, meta_file), 'w', newline='') as meta_csv:
            csv_writer = csv.writer(meta_csv)
            csv_writer.writerow(['Task', 'Sensor', 'Date', 'Timestamp', 'Name', 'Contact_No',
                                 'Location', 'Gender', 'Age', 'Spectacles', 'Run', 'FPS', 'Time_to_capture', 'Classes', 'Road', 'Traffic', 'disturbance_TT', 'Comments', 'Trail_flag', 'Test_flag'])
            csv_writer.writerow([task,
                                 sensor,
                                 datetime.datetime.now().date(),
                                 t_stamp,
                                 user_configuration['name'],
                                 user_configuration['contact_number'],
                                 user_configuration['location'],
                                 user_configuration['gender'],
                                 user_configuration['age'],
                                 user_configuration['spectacles'],
                                 user_configuration['run'],
                                 fps,
                                 toc,
                                 classes,
                                 road_condition,
                                 traffic_condition,
                                 electronic_disturbance,
                                 content])

    else:
        with open(os.path.join(meta_path, meta_file), 'a', newline='') as meta_csv:
            csv_writer = csv.writer(meta_csv)
            csv_writer.writerow([task,
                                 sensor,
                                 datetime.datetime.now().date(),
                                 t_stamp,
                                 user_configuration['name'],
                                 user_configuration['contact_number'],
                                 user_configuration['location'],
                                 user_configuration['gender'],
                                 user_configuration['age'],
                                 user_configuration['spectacles'],
                                 user_configuration['run'],
                                 fps,
                                 toc,
                                 classes,
                                 road_condition,
                                 traffic_condition,
                                 electronic_disturbance,
                                 content])


def add_comments(content, classes, fps, toc, road_condition, traffic_condition, electronic_disturbance):
    t = str(time.time())
    t_stamp = t.replace('.', '-')
    meta_file = 'metadata_v1.csv'
    meta_path = os.path.join(current_path, 'metadata')
    os.makedirs(meta_path, exist_ok=True)

    if not os.path.exists(os.path.join(meta_path, meta_file)):
        with open(os.path.join(meta_path, meta_file), 'w', newline='') as meta_csv:
            csv_writer = csv.writer(meta_csv)
            csv_writer.writerow(['Task', 'Sensor', 'Date', 'Timestamp', 'Name', 'Contact_No',
                                 'Location', 'Gender', 'Age', 'Spectacles', 'Run', 'FPS', 'Time_to_capture', 'Classes', 'Road', 'Traffic', 'disturbance_TT', 'Comments', 'Trail_flag', 'Test_flag'])
            csv_writer.writerow([task_and_sensor_info["task"],
                                 task_and_sensor_info["sensor"],
                                 datetime.datetime.now().date(),
                                 t_stamp,
                                 user_configuration['name'],
                                 user_configuration['contact_number'],
                                 user_configuration['location'],
                                 user_configuration['gender'],
                                 user_configuration['age'],
                                 user_configuration['spectacles'],
                                 user_configuration['run'],
                                 fps,
                                 toc,
                                 classes,
                                 road_condition,
                                 traffic_condition,
                                 electronic_disturbance,
                                 content])

    else:
        with open(os.path.join(meta_path, meta_file), 'a', newline='') as meta_csv:
            csv_writer = csv.writer(meta_csv)
            csv_writer.writerow([task_and_sensor_info["task"],
                                 task_and_sensor_info["sensor"],
                                 datetime.datetime.now().date(),
                                 t_stamp,
                                 user_configuration['name'],
                                 user_configuration['contact_number'],
                                 user_configuration['location'],
                                 user_configuration['gender'],
                                 user_configuration['age'],
                                 user_configuration['spectacles'],
                                 user_configuration['run'],
                                 fps,
                                 toc,
                                 classes,
                                 road_condition,
                                 traffic_condition,
                                 electronic_disturbance,
                                 content])


def add_comments_ir_rgb(content, classes, fps, toc, road_condition, traffic_condition, electronic_disturbance, s1):
    meta_file = 'metadata_v1.csv'
    meta_path = os.path.join(current_path, 'metadata')
    os.makedirs(meta_path, exist_ok=True)

    if not os.path.exists(os.path.join(meta_path, meta_file)):
        with open(os.path.join(meta_path, meta_file), 'w', newline='') as meta_csv:
            csv_writer = csv.writer(meta_csv)
            csv_writer.writerow(['Task', 'Sensor', 'Date', 'Timestamp', 'Name', 'Contact_No',
                                 'Location', 'Gender', 'Age', 'Spectacles', 'Run', 'FPS', 'Time_to_capture', 'Classes', 'Road', 'Traffic', 'disturbance_TT', 'Comments', 'Trail_flag', 'Test_flag'])
            for s in s1:
                t = str(time.time())
                t_stamp = t.replace('.', '-')
                csv_writer.writerow([task_and_sensor_info["task"],
                                     s,
                                     datetime.datetime.now().date(),
                                     t_stamp,
                                     user_configuration['name'],
                                     user_configuration['contact_number'],
                                     user_configuration['location'],
                                     user_configuration['gender'],
                                     user_configuration['age'],
                                     user_configuration['spectacles'],
                                     user_configuration['run'],
                                     fps,
                                     toc,
                                     classes,
                                     road_condition,
                                     traffic_condition,
                                     electronic_disturbance,
                                     content])
                time.sleep(0.1)

    else:
        with open(os.path.join(meta_path, meta_file), 'a', newline='') as meta_csv:
            csv_writer = csv.writer(meta_csv)
            for s in s1:
                t = str(time.time())
                t_stamp = t.replace('.', '-')
                csv_writer.writerow([task_and_sensor_info["task"],
                                     s,
                                     datetime.datetime.now().date(),
                                     t_stamp,
                                     user_configuration['name'],
                                     user_configuration['contact_number'],
                                     user_configuration['location'],
                                     user_configuration['gender'],
                                     user_configuration['age'],
                                     user_configuration['spectacles'],
                                     user_configuration['run'],
                                     fps,
                                     toc,
                                     classes,
                                     road_condition,
                                     traffic_condition,
                                     electronic_disturbance,
                                     content])
                time.sleep(0.1)


def get_audio_configuration():
    prompt = (
        '\nEnter recording details  (e.g., 1111): \n'
        ' Engine mode 1: engine_on, 0: engine_off \n'
        ' Windows     1: closed,    0: open \n'
        ' Music       1: music_on,  0: music_off \n'
        ' Number of occupants : 1 to 5 \n'
        ' Example input: 1111 \n'
    )

    valid_input_first_three = ['0', '1']
    valid_input_last = ['1', '2', '3', '4', '5']

    while True:
        audio_bit_user_input = input(prompt)
        if (
                len(audio_bit_user_input) == 4 and
                all(bit in valid_input_first_three for bit in audio_bit_user_input[:3]) and
                audio_bit_user_input[3] in valid_input_last
        ):
            engine_mode = 'engine_on' if audio_bit_user_input[0] == '1' else 'engine_off'
            windows = 'closed' if audio_bit_user_input[1] == '1' else 'open'
            music = 'music_on' if audio_bit_user_input[2] == '1' else 'music_off'
            occupants = audio_bit_user_input[3]  # Directly take the number of occupants from input
            t = str(time.time())
            time_stamp = t.replace('.', '-')

            return {
                'audio_name': time_stamp,
                'engine_mode': engine_mode,
                'windows': windows,
                'music': music,
                'occupants': occupants,
                'bits': audio_bit_user_input
            }
        else:
            print("Invalid input. Please enter a 4-bit flag in the format specified.")


def save_to_csv(csv_file, timestamp, user_configuration, comment):
    with open(csv_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, user_configuration['audio_name'], user_configuration['engine_mode'],
                         user_configuration['windows'], user_configuration['music'], user_configuration['occupants'], comment])
