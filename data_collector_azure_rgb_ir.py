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

# Set to 1 if rotation by 180 degree is needed.
rotate_flag = 1

# Set this to 1 for annotations, if 0 the data collection continues
annotations_flag = 1

# number of bounding boxes in 1 frame.
number_of_subjects = 1

# Replace with your actual class labels
class_names = ['FOCUSED', 'SLEEPY', 'DISTRACTED']

# Time in sec, if 0 then use 'S' to stop the code
time_to_capture = 10

# Change file_extension, to 'npy' to save raw data
file_extension = 'jpeg'
file_extension_annotations = 'txt'

# Initialize the library, if the library is not found, add the library path as argument
pykinect.initialize_libraries()
# Modify camera configuration
device_config = pykinect.default_configuration
device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1080P
device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED
device_config.camera_fps = pykinect.K4A_FRAMES_PER_SECOND_30

# Start device
device = pykinect.start_device(config=device_config)

sensor_1 = 'azure_ir'
sensor_2 = 'azure_rgb'

path_ir = initialize_details(sensor_1)
path_rgb = path_ir.replace(sensor_1, sensor_2)
os.makedirs(path_rgb, exist_ok=True)

alpha = 0.2  # Contrast control
beta = 0.09  # Brightness control

s_list = [sensor_1, sensor_2]

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
            pass

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
            pass

        if rotate_flag:
            # Rotate the frame by 180 degree
            rgb = cv2.rotate(rgb, cv2.ROTATE_180)

        # Annotate the frame using the annotator module
        annotator.annotate_frame(rgb)
        rgb_annotation_string.append(annotator.annotation_string)
        print(rgb_annotation_string)
        counter += 1


def azure_data():
    frame_count = 0
    cv2.namedWindow('Infrared Image', cv2.WINDOW_NORMAL)
    cv2.namedWindow('RGB Image', cv2.WINDOW_NORMAL)
    start_time = time.time()  # set timer

    while True:
        # Get frames from azure.
        capture = device.update()

        # Get the infrared image
        ret, ir_image = capture.get_ir_image()
        ir_image = ir_image.astype(np.int32)

        # Get RGB image
        ret_rgb, rgb_image = capture.get_color_image()

        if not ret or not ret_rgb:
            pass

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

        print(data_i)
        print(data_r)

        if rotate_flag:
            # Rotate the frame by 180 degree
            rgb_image = cv2.rotate(rgb_image, cv2.ROTATE_180)
            ir_image = cv2.rotate(ir_image, cv2.ROTATE_180)

        # call convertScaleAbs function, just for visualisation
        adjusted_ir = cv2.convertScaleAbs(ir_image, alpha=alpha, beta=beta)
        cv2.imshow('IR Image', adjusted_ir)
        cv2.imshow('RGB Image', rgb_image)

        # check file extension and save accordingly
        if file_extension != 'npy':
            cv2.imwrite(data_i, adjusted_ir)
            cv2.imwrite(data_r, rgb_image)
        else:
            np.save(data_i, ir_image)
            np.save(data_r, rgb_image)

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
            if time.time() - start_time >= time_to_capture:
                fps = frame_count / (time.time() - start_time)
                print(time.time() - start_time)
                print(f'FPS: {fps}')
                comment = input('Enter Comments:')
                add_comments_ir_rgb(comment, s_list)
                exit()

        # Stop when 'S' is pressed
        if cv2.waitKey(1) == ord('s'):
            fps = frame_count / (time.time() - start_time)
            print(time.time() - start_time)
            print(f'FPS: {fps}')
            comment = input('Enter Comments:')
            add_comments_ir_rgb(comment, s_list)
            exit()


azure_data()
