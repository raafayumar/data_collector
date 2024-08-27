"""

    This code was created by Raafay Umar on 04-11-2023.

    an example code showing the use of 'initializer' module

    to collect Data using Azure RGB and IR.

    this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”


"""

from initializer import initialize_details, file_constructor, ImageAnnotator, add_comments_ir_rgb
import os
import time
import pykinect_azure as pykinect
import cv2
import numpy as np
import threading
from rich.console import Console
from rich.table import Table
import argparse

# Argument parser setup
parser = argparse.ArgumentParser(description="Collect data using Azure RGB and IR.")
parser.add_argument("--load_task", type=str, default='y', help="Load previous Task details? To continue press Y, To change press N")
parser.add_argument("--load_details", type=str, default='y', help="Load previous subject details? To continue press Y, To change press N")
parser.add_argument("--rotate", type=int, default=1, help="Set to 1 if rotation by 180 degrees is needed.")
parser.add_argument("--annotations", type=int, default=0, help="Set this to 1 for annotations, 0 to continue data collection.")
parser.add_argument("--subjects", type=int, default=1, help="Number of bounding boxes in one frame.")
parser.add_argument("--time", type=int, default=10, help="Time to capture in seconds. If 0, use 'S' to stop the code.")
args = parser.parse_args()

console = Console()

# Set to 1 if rotation by 180 degree is needed.
rotate_flag = args.rotate

# Set this to 1 for annotations, if 0 the data collection continues
annotations_flag = args.annotations

# number of bounding boxes in 1 frame.
number_of_subjects = args.time

# Time in sec, if 0 then use 'S' to stop the code
time_to_capture = args.time

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

conditions = '0000'
classes = '0000'

path_ir = initialize_details(sensor_1, args.load_task, args.load_details)
path_rgb = path_ir.replace(sensor_1, sensor_2)
os.makedirs(path_rgb, exist_ok=True)

alpha = 0.2  # Contrast control
beta = 0.09  # Brightness control

temp = path_ir.split('\\')
task = temp[temp.index('datafolder') + 1]

if task == 'driver_face':
    class_names = ['FOCUSED', 'SLEEPY', 'DISTRACTED']

elif task == 'seat_belt':
    class_names = ['with_sb', 'without_sb', 'twisted_sb', 'back_sb', 'oblap_sb', 'obchest_sb', 'oblap_bsb', 'obchest_bsb',
                   'reflect_sb',
                   'tape_sb', 'loose_sb']
else:
    class_names = ['Add your classes!']

road_condition = traffic_condition = road_condition_text = traffic_condition_text = disturbance = 'None'

s_list = [sensor_1, sensor_2]

if not annotations_flag:
    road_condition = input('\nPlease select road condition.\nGood road:0, Moderate road:1, Bad road:2\n')
    traffic_condition = input('\nPlease select traffic condition.\nMild:0, Moderate:1, Heavy:2\n')

    road_conditions = {'0': 'Good road', '1': 'Moderate road', '2': 'Bad road'}
    traffic_conditions = {'0': 'Mild traffic', '1': 'Moderate traffic', '2': 'Heavy traffic'}

    road_condition_text = road_conditions.get(road_condition, 'Unknown road condition')
    traffic_condition_text = traffic_conditions.get(traffic_condition, 'Unknown traffic condition')

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

        if not ret:
            continue

        ir = ir.astype(np.int32)

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


def save_image(filename, img):
    # check file extension and save accordingly
    if file_extension != 'npy':
        cv2.imwrite(filename, img)
    else:
        np.save(filename, img)


def azure_data():
    frame_count = 0
    class_num = 'None'
    cv2.namedWindow('IR Image', cv2.WINDOW_NORMAL)
    cv2.namedWindow('RGB Image', cv2.WINDOW_NORMAL)
    sl_no = 1
    start_time = time.time()  # set timer
    while True:
        table = Table(title="Details of the run")

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
            str(s_list_formatted),
            str(lux_value),
            str(run),
            str(frame_count)
        )

        console.clear()
        console.print(table)

        sl_no += 1

        if rotate_flag:
            # Rotate the frame by 180 degree
            rgb_image = cv2.rotate(rgb_image, cv2.ROTATE_180)
            ir_image = cv2.rotate(ir_image, cv2.ROTATE_180)

        # call convertScaleAbs function, just for visualisation
        adjusted_ir = cv2.convertScaleAbs(ir_image, alpha=alpha, beta=beta)
        cv2.imshow('IR Image', adjusted_ir)
        cv2.imshow('RGB Image', rgb_image)

        threading.Thread(target=save_image, args=(data_i, adjusted_ir)).start()
        threading.Thread(target=save_image, args=(data_r, rgb_image)).start()

        if annotations_flag:
            anno_file = f'{path_r}_{frame_count:07d}.{file_extension_annotations}'
            anno_data = os.path.join(path_r, anno_file)
            with open(anno_data, 'w') as file:
                if type(rgb_annotation_string) == list:
                    previous_class_name = None
                    final_string = ''

                    for i in range(0, number_of_subjects):
                        temp = rgb_annotation_string[i].split(" ")
                        current_class_name = class_names[int(temp[0])]

                        if previous_class_name is not None:
                            concatenated_class_name = previous_class_name + '-' + current_class_name
                            final_string += concatenated_class_name + ' '
                        else:
                            final_string += current_class_name + ' '

                        previous_class_name = current_class_name

                    # Trim the trailing space
                    class_num = final_string.strip()
                else:
                    file.write(rgb_annotation_string)
                    class_num = class_num[int(rgb_annotation_string[0])]

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
            if time.time() - start_time >= time_to_capture:
                fps = frame_count / (time.time() - start_time)
                print(time.time() - start_time)
                print(f'FPS: {fps}')
                comment = input('Enter Comments:')
                device.close()
                add_comments_ir_rgb(comment, class_num, fps, time_to_capture, road_condition, traffic_condition, disturbance,
                                    s_list)
                exit()

        # Stop when 'S' is pressed
        if cv2.waitKey(1) == ord('s'):
            fps = frame_count / (time.time() - start_time)
            print(time.time() - start_time)
            print(f'FPS: {fps}')
            comment = input('Enter Comments:')
            device.close()
            add_comments_ir_rgb(comment, class_num, fps, time_to_capture, road_condition, traffic_condition, disturbance, s_list)
            exit()


azure_data()
