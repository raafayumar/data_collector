"""

    This code was created by Raafay Umar on 04-11-2023.

    an example code showing the use of 'initializer' module

    to collect Data using Azure RGB and IR.

    this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”


"""
import initializer
from initializer import initialize_details, file_constructor, ImageAnnotator, add_comments_ir_rgb, \
    get_audio_configuration, send_trigger, add_comments_all
import os
import time
import pykinect_azure as pykinect
import cv2
import numpy as np
import sounddevice
from scipy.io.wavfile import write
import datetime
import threading
from rich.console import Console
from rich.table import Table
from open_application import check_application

check_application()
console = Console()

# Set to 1 if rotation by 180 degree is needed.
rotate_flag = 1

# Set this to 1 for annotations, if 0 the data collection continues
annotations_flag = 0

# number of bounding boxes in 1 frame.
number_of_subjects = 1

# Replace with your actual class labels
class_names = ['FOCUSED', 'SLEEPY', 'DISTRACTED']

# Time in sec, if 0 then use 'S' to stop the code
time_to_capture = int(input('\nPlease enter\nTime to capture in Seconds:'))

# Change file_extension, to 'npy' to save raw data
file_extension = 'jpeg'
file_extension_annotations = 'txt'

# Initialize the library, if the library is not found, add the library path as argument
pykinect.initialize_libraries()
# Modify camera configuration
device_config = pykinect.default_configuration
device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_720P
device_config.color_format = pykinect.K4A_IMAGE_FORMAT_COLOR_YUY2
device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED
device_config.camera_fps = pykinect.K4A_FRAMES_PER_SECOND_30

# Start device
device = pykinect.start_device(config=device_config)

sensor_1 = 'azure_ir'
sensor_2 = 'azure_rgb'

path_ir = initialize_details(sensor_1)
path_rgb = path_ir.replace(sensor_1, sensor_2)
os.makedirs(path_rgb, exist_ok=True)

audio_data = get_audio_configuration()

alpha = 0.2  # Contrast control
beta = 0.09  # Brightness control

s_list = [sensor_1, sensor_2]

road_condition = str(input('\nPlease select road condition.\nGood road:0, Moderate road:1, Bad road:2\n'))

traffic_condition = str(input('\nPlease select traffic condition.\nMild:0, Moderate:1, Heavy:2\n'))

disturbance = 'None'

flag = 1

vayyar_fps = 0.0
dash_fps = 0.0

classes = 0
conditions = int(road_condition + traffic_condition)
sl_no = 1  # Starting serial number

# Create variables based on user inputs
if road_condition == '0':
    road_condition_text = "Good"
elif road_condition == '1':
    road_condition_text = "Moderate"
elif road_condition == '2':
    road_condition_text = "Bad"
else:
    road_condition_text = "Unknown road condition"

if traffic_condition == '0':
    traffic_condition_text = "Mild"
elif traffic_condition == '1':
    traffic_condition_text = "Moderate"
elif traffic_condition == '2':
    traffic_condition_text = "Heavy"
else:
    traffic_condition_text = "Unknown traffic condition"

if annotations_flag:
    ir_annotation_string = []
    counter = 0
    while counter < number_of_subjects:
        # create an object of ImageAnnotator class
        annotator = ImageAnnotator()
        annotator.set_class_names(class_names)

        # Get 1 IR frame for annotation
        capture_anno = device.update()
        ret, ir = capture_anno.get_ir_image()
        ir = ir.astype(np.int32)

        if not ret:
            continue

        if rotate_flag:
            # Rotate the frame by 180 degree
            ir = cv2.rotate(ir, cv2.ROTATE_180)

        adjusted_anno = cv2.convertScaleAbs(ir, alpha=alpha, beta=beta)

        # Annotate the frame using the annotator module
        annotator.annotate_frame(adjusted_anno)
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
        capture_anno = device.update()
        ret, rgb = capture_anno.get_color_image()

        if not ret:
            continue

        if rotate_flag:
            # Rotate the frame by 180 degree
            rgb = cv2.rotate(rgb, cv2.ROTATE_180)

        # Annotate the frame using the annotator module
        annotator.annotate_frame(rgb)
        rgb_annotation_string.append(annotator.annotation_string)
        print(rgb_annotation_string)
        counter += 1


def save_image_intel(filename, img):
    # check file extension and save accordingly
    if file_extension != 'npy':
        cv2.imwrite(filename, img)
    else:
        np.save(filename, img)


def save_image(filename, img):
    # check file extension and save accordingly
    if file_extension != 'npy':
        cv2.imwrite(filename, img)
    else:
        np.save(filename, img)


def print_table(path, time_remaining, sl_no,  frame_count):
    table = Table(title="Details of the run")

    parts = str(os.path.split(path)[-1]).split('_')
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


def azure_data():
    global flag, disturbance
    frame_count = 0
    sl_no = 1
    cv2.namedWindow('IR Image', cv2.WINDOW_NORMAL)
    # cv2.namedWindow('RGB Image', cv2.WINDOW_NORMAL)

    start_time = time.time()  # set timer
    while True:
        # Get frames from azure.
        capture = device.update()

        # Get the infrared image
        ret, ir_image = capture.get_ir_image()

        # Get RGB image
        ret_rgb, rgb_image = capture.get_color_image()

        if not ret or not ret_rgb:
            continue

        ir_image = ir_image.astype(np.int32)

        # get the constructed file name, with lux values for Azure IR
        name_i = file_constructor(conditions, classes)
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

        threading.Thread(target=print_table, args=(path_i, time_remaining, sl_no, frame_count)).start()

        sl_no += 1

        if rotate_flag:
            # Rotate the frame by 180 degree
            rgb_image = cv2.rotate(rgb_image, cv2.ROTATE_180)
            ir_image = cv2.rotate(ir_image, cv2.ROTATE_180)

        # call convertScaleAbs function, just for visualisation
        adjusted_ir = cv2.convertScaleAbs(ir_image, alpha=alpha, beta=beta)
        cv2.imshow('IR Image', adjusted_ir)
        # cv2.imshow('RGB Image', rgb_image)

        threading.Thread(target=save_image, args=(data_i, adjusted_ir)).start()
        threading.Thread(target=save_image, args=(data_r, rgb_image)).start()

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
            if time.time() - start_time >= (time_to_capture / 2) and flag:
                t = str(time.time())
                temp = t.replace('.', '-')
                disturbance = temp+'/'+str(frame_count)
                send_trigger()
                flag = 0

            if time.time() - start_time >= time_to_capture:
                fps = frame_count / (time.time() - start_time)
                time.sleep(2)
                print(f'Azure FPS: {fps}\nVayyar FPS: {vayyar_fps}\nDashcam FPS: {dash_fps}')
                comment = input('\n\nEnter Comments:')
                device.close()
                add_comments_ir_rgb(comment, 'None', fps, time_to_capture, road_condition_text, traffic_condition_text, disturbance, s_list)
                exit()

        # Stop when 'S' is pressed
        if cv2.waitKey(1) == ord('s'):
            fps = frame_count / (time.time() - start_time)
            print(time.time() - start_time)
            print(f'FPS: {fps}')
            comment = input('Enter Comments:')
            add_comments_ir_rgb(comment, 'None', fps, time_to_capture, road_condition_text, traffic_condition_text, disturbance,
                                s_list)
            exit()


def record_audio(sample_rate=44100, channels=1):
    path_audio = path_rgb.replace(sensor_2, 'mic').replace('driver_face', 'audio')
    os.makedirs(path_audio, exist_ok=True)

    file_name = file_constructor(conditions, int(audio_data['bits']))
    path_v = os.path.join(path_audio, file_name)

    # construct the final file name
    file_name_i = f'{path_v}_0000000.wav'
    output_file = os.path.join(path_v, file_name_i)

    recorded_voice = sounddevice.rec(int(time_to_capture * sample_rate), samplerate=sample_rate, channels=channels)
    sounddevice.wait()
    write(output_file, sample_rate, recorded_voice)
    add_comments_all('audio', 'mic', 'None', '0', time_to_capture, str(audio_data['bits']), road_condition_text,
                     traffic_condition_text,
                     disturbance)


def vayyar_data():
    global vayyar_fps
    from get_vayyar import config_vayyar, get_vayyar_data
    config_vayyar()

    path_vayyar = path_rgb.replace(sensor_2, 'vayyar').replace('driver_face', 'occupant')
    os.makedirs(path_vayyar, exist_ok=True)

    frame_count = 0
    start_time = time.time()

    while True:
        file_name = file_constructor(conditions, classes)
        path_v = os.path.join(path_vayyar, file_name)

        # construct the final file name
        file_name_i = f'{path_v}_{frame_count:07d}.csv'
        data_v = os.path.join(path_v, file_name_i)

        get_vayyar_data(data_v)

        frame_count += 1

        if time.time() - start_time >= (0.25 * time_to_capture):
            vayyar_fps = frame_count / (time.time() - start_time)
            add_comments_all('occupant', 'vayyar', 'None', vayyar_fps, time_to_capture, 'None',
                             road_condition_text, traffic_condition_text,
                             disturbance)
            break


def dashcam():
    global dash_fps
    # Initialize other RGB camera
    cam = cv2.VideoCapture(1)
    cv2.namedWindow('INTEL Image', cv2.WINDOW_NORMAL)

    path_intel = path_rgb.replace(sensor_2, 'intel_rgb').replace('driver_face', 'dashcam')
    os.makedirs(path_intel, exist_ok=True)

    frame_count = 0
    start_time = time.time()
    while True:
        ret_i, intel = cam.read()

        if not ret_i:
            continue

        if rotate_flag:
            # Rotate the frame by 180 degree
            intel = cv2.rotate(intel, cv2.ROTATE_180)

        # get the constructed file name, with lux values for Intel camera.
        name = file_constructor(conditions, classes)
        path = os.path.join(path_intel, name)

        # construct the final file name
        file_name = f'{path}_{frame_count:07d}.{file_extension}'
        data = os.path.join(path, file_name)

        threading.Thread(target=save_image_intel, args=(data, intel)).start()

        frame_count += 1

        cv2.imshow('INTEL Image', intel)

        if cv2.waitKey(1) == ord('q'):
            break

        if time.time() - start_time >= time_to_capture:
            dash_fps = frame_count / (time.time() - start_time)
            add_comments_all('dashcam', 'intel_rgb', 'None', dash_fps, time_to_capture, 'None', road_condition_text,
                             traffic_condition_text,
                             disturbance)
            break


def get_imu():
    from get_imu import create_csv, imu_data
    import initializer
    datefolder = str(datetime.datetime.now().date())

    path_imu = os.path.join(initializer.current_path, 'imu_data', datefolder)
    os.makedirs(path_imu, exist_ok=True)

    name = file_constructor(conditions, classes)
    data = os.path.join(path_imu, name)
    filename = f'{data}_0000000.csv'

    create_csv(filename)
    start_time = time.time()
    while True:
        imu_data(filename)

        if time.time() - start_time >= time_to_capture:
            break


audio_data_capture = threading.Thread(target=record_audio)
audio_data_capture.start()

azure_data_capture = threading.Thread(target=azure_data)
azure_data_capture.start()

dash_cam = threading.Thread(target=dashcam)
dash_cam.start()

imu = threading.Thread(target=get_imu)
imu.start()

vayyar = threading.Thread(target=vayyar_data)
vayyar.start()
