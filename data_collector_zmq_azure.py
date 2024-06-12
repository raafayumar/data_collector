"""

    This code was created by Raafay Umar on 19-11-2023.

    an example code showing the use of 'initializer' module.

    this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”


"""

import initializer
from initializer import initialize_details, file_constructor, ImageAnnotator, add_comments_ir_rgb, get_audio_configuration, send_trigger
import os
import numpy as np
import time
import cv2
import zmq
import sounddevice
from scipy.io.wavfile import write
from datetime import datetime
import threading
from rich.console import Console
from rich.table import Table

console = Console()

sl_no = 1  # Starting serial number

# Set this to 1 for annotations, if 0 the data collection continues
annotations_flag = 0

# number of bounding boxes in 1 frame.
number_of_subjects = 1

# Replace with your actual class labels
class_names = ['FOCUSED', 'SLEEPY', 'DISTRACTED']

# Time in sec, if 0 then use 'S' to stop the code
time_to_capture = 10

# Change file_extension, to 'npy' to save raw data
file_extension = 'jpeg'
file_extension_annotations = 'txt'

sensor_1 = 'azure_ir'
sensor_2 = 'azure_rgb'

path_ir = initialize_details(sensor_1)
path_rgb = path_ir.replace(sensor_1, sensor_2)
os.makedirs(path_rgb, exist_ok=True)

audio_data = get_audio_configuration()

alpha = 0.2  # Contrast control
beta = 0.09  # Brightness control

s_list = [sensor_1, sensor_2]

road_condition = input('\nPlease select road condition.\nGood road:0, Moderate road:1, Bad road:2\n')

traffic_condition = input('\nPlease select traffic condition.\nMild:0, Moderate:1, Heavy:2\n')


# Create variables based on user inputs
if road_condition == '0':
    road_condition_text = "Good road"
elif road_condition == '1':
    road_condition_text = "Moderate road"
elif road_condition == '2':
    road_condition_text = "Bad road"
else:
    road_condition_text = "Unknown road condition"

if traffic_condition == '0':
    traffic_condition_text = "Mild traffic"
elif traffic_condition == '1':
    traffic_condition_text = "Moderate traffic"
elif traffic_condition == '2':
    traffic_condition_text = "Heavy traffic"
else:
    traffic_condition_text = "Unknown traffic condition"

disturbance = 'None'

# Setup ZeroMQ context and socket
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://192.168.0.3:5555")
socket.setsockopt(zmq.SUBSCRIBE, b'RGB')
socket.setsockopt(zmq.SUBSCRIBE, b'IR')
socket.setsockopt(zmq.RCVHWM, 1)  # Set high watermark to 1 to avoid buffering

flag = 1

if annotations_flag:
    ir_annotation_string = []
    counter = 0
    while counter < number_of_subjects:
        # create an object of ImageAnnotator class
        annotator = ImageAnnotator()
        annotator.set_class_names(class_names)

        # Get 1 IR frame for annotation
        ft, fb = socket.recv_multipart()
        f = cv2.imdecode(np.frombuffer(fb, dtype=np.uint8), cv2.IMREAD_COLOR)

        if ft == b"IR":
            ir = f
        else:
            ir = None

        # Annotate the frame using the annotator module
        annotator.annotate_frame(ir)
        ir_annotation_string.append(annotator.annotation_string)
        print(ir_annotation_string)
        counter += 1

if annotations_flag:
    counter = 0
    rgb_annotation_string = []
    while counter < number_of_subjects:
        # create an object of ImageAnnotator class
        annotator = ImageAnnotator()
        annotator.set_class_names(class_names)

        # Get 1 RGB image for annotation
        # Get 1 IR frame for annotation
        ft, fb = socket.recv_multipart()
        f = cv2.imdecode(np.frombuffer(fb, dtype=np.uint8), cv2.IMREAD_COLOR)

        if ft == b"RGB":
            rgb = f
        else:
            rgb = None

        # Annotate the frame using the annotator module
        annotator.annotate_frame(rgb)
        rgb_annotation_string.append(annotator.annotation_string)
        print(rgb_annotation_string)
        counter += 1

ir_image = None
rgb_image = None


# Function to drain the queue and keep the latest message for each topic
def drain_queue(socket):
    latest_rgb = None
    latest_ir = None
    while True:
        try:
            topic, img_buffer = socket.recv_multipart(zmq.NOBLOCK)
            if topic == b'RGB':
                latest_rgb = (topic, img_buffer)
            elif topic == b'IR':
                latest_ir = (topic, img_buffer)
        except zmq.Again:
            break
    return latest_rgb, latest_ir


# Initial queue drain to clear out any messages that were received during setup
drain_queue(socket)


def azure_data():
    global rgb_image, ir_image, flag, disturbance, stop_flag
    frame_count = 0
    sl_no = 1
    cv2.namedWindow('Infrared Image', cv2.WINDOW_NORMAL)
    cv2.namedWindow('RGB Image', cv2.WINDOW_NORMAL)

    start_time = time.time()  # set timer
    while True:
        try:
            table = Table(title="Details of the run")

            latest_rgb, latest_ir = drain_queue(socket)  # Clear out old messages and get the latest ones

            # get the constructed file name, with lux values for Azure IR
            name_i = file_constructor()
            path_i = os.path.join(path_ir, name_i)

            # construct the final file name
            file_name_i = f'{path_i}_{frame_count:07d}.{file_extension}'
            data_i = os.path.join(path_i, file_name_i)

            # Path and file name for Azure RGB
            path_r = os.path.join(path_rgb, name_i)

            # construct the final file name
            file_name_r = f'{path_r}_{frame_count:07d}.{file_extension}'
            data_r = os.path.join(path_r, file_name_r)

            time_remaining = str(int(time_to_capture - (time.time() - start_time)))

            parts = str(os.path.split(path_i)[-1]).split('_')
            s_list_formatted = "\n".join([str(item) for item in s_list])
            lux_value = parts[7]
            name = parts[1]
            run = parts[-1]

            if parts[7] == '00000':
                lux_value = 'Check LUX'

            table.add_column("Sl No", justify="right", style="cyan", no_wrap=True)
            table.add_column("Subject", justify="right", style="cyan")
            table.add_column("Time Remaining", justify="right", style="cyan")
            table.add_column("Road Condition", justify="right", style="cyan")
            table.add_column("Traffic Condition", justify="right", style="cyan")
            table.add_column("Audio Config bit", justify="right", style="cyan")
            table.add_column("Sensors", justify="right", style="cyan")
            table.add_column("Lux", justify="right", style="red")
            table.add_column("Run", justify="right", style="cyan")
            table.add_column("Frame", justify="right", style="cyan")

            table.add_row(
                str(sl_no),
                str(name),
                time_remaining,
                road_condition_text,
                traffic_condition_text,
                str(audio_data['bits']),
                str(s_list_formatted),
                str(lux_value),
                str(run),
                str(frame_count)
            )

            console.clear()
            console.print(table)

            sl_no += 1

            if latest_rgb:
                topic, img_buffer = latest_rgb
                img_array = np.frombuffer(img_buffer, dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if img is not None:
                    rgb_image = img
                    threading.Thread(target=save_image, args=(data_r, rgb_image)).start()
                else:
                    print("Failed to decode RGB image")

            if latest_ir:
                topic, img_buffer = latest_ir
                img_array = np.frombuffer(img_buffer, dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if img is not None:
                    ir_image = img
                    threading.Thread(target=save_image, args=(data_i, ir_image)).start()
                else:
                    print("Failed to decode IR image")

            cv2.imshow('IR Image', ir_image)
            cv2.imshow('RGB Image', rgb_image)

            if annotations_flag:
                anno_file = f'{path_r}_{frame_count:07d}.{file_extension_annotations}'
                anno_data = os.path.join(path_r, anno_file)
                with open(anno_data, 'w') as file:
                    if type(rgb_annotation_string) == list:
                        for i in range(0, number_of_subjects):
                            # Write annotation data to the file
                            file.write(rgb_annotation_string[i] + '\n')
                    else:
                        file.write(rgb_annotation_string)

            if annotations_flag:
                anno_file1 = f'{path_i}_{frame_count:07d}.{file_extension_annotations}'
                anno_data1 = os.path.join(path_i, anno_file1)
                with open(anno_data1, 'w') as file:
                    if type(ir_annotation_string) == list:
                        for i in range(0, number_of_subjects):
                            # Write annotation data to the file
                            file.write(ir_annotation_string[i] + '\n')
                    else:
                        file.write(ir_annotation_string)

            frame_count += 1  # frame counter

            if cv2.waitKey(1) == ord('q'):
                break

            # Stop after 10 sec
            if time_to_capture != 0:
                if time.time() - start_time >= (time_to_capture/2) and flag:
                    disturbance = time.time()
                    send_trigger()
                    flag = 0

                if time.time() - start_time >= time_to_capture:
                    fps = frame_count / (time.time() - start_time)
                    print(time.time() - start_time)
                    print(f'FPS: {fps}')
                    comment = input('Enter Comments:')
                    add_comments_ir_rgb(comment, road_condition, traffic_condition, disturbance, s_list)
                    stop_flag = 1
                    exit()

            # Stop when 'S' is pressed
            if cv2.waitKey(1) == ord('s'):
                fps = frame_count / (time.time() - start_time)
                print(time.time() - start_time)
                print(f'FPS: {fps}')
                comment = input('Enter Comments:')
                add_comments_ir_rgb(comment, road_condition, traffic_condition, disturbance, s_list)
                stop_flag = 1
                exit()

        except Exception as e:
            print(f"An error occurred: {e}")
            continue


def save_image(filename, img):
    # check file extension and save accordingly
    if file_extension != 'npy':
        cv2.imwrite(filename, img)
    else:
        np.save(filename, img)


def record_audio(sample_rate=44100, channels=1):
    # Create folder based on the current date
    date_folder = datetime.now().strftime("%Y-%m-%d")
    output_directory = os.path.join(initializer.current_path, "audio_data", date_folder)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_directory, f"{audio_data['audio_name']}_{audio_data['engine_mode']}_{audio_data['windows']}_{audio_data['music']}_{audio_data['occupants']}_{timestamp}.wav")

    recorded_voice = sounddevice.rec(int(time_to_capture * sample_rate), samplerate=sample_rate, channels=channels)
    sounddevice.wait()
    write(output_file, sample_rate, recorded_voice)


azure_data_capture = threading.Thread(target=azure_data)
audio_data_capture = threading.Thread(target=record_audio)

azure_data_capture.start()
audio_data_capture.start()
