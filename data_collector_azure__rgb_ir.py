"""

    This code was created by Raafay Umar on 04-11-2023.

    an example code showing the use of 'initializer' module

    to collect Data using Azure RGB and IR.

    this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”


"""

from initializer import initialize_details, file_constructor, ImageAnnotator
import os
import time
import pykinect_azure as pykinect
import cv2
import threading
import numpy as np

# Set to 1 if rotation by 180 degree is needed.
rotate_flag = 0

# Set this to 1 for annotations, if 0 the data collection continues
annotations_flag = 1
class_names = ['Focused', 'Sleepy', 'Distraction']  # Replace with your actual class labels

# Time in sec
time_to_capture = 10

# Change file_extension, to 'npy' to save raw data
file_extension = 'png'
file_extension_annotations = 'txt'

# Initialize the library, if the library is not found, add the library path as argument
pykinect.initialize_libraries()
# Modify camera configuration
device_config = pykinect.default_configuration
device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1080P
device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED

# Start device
device = pykinect.start_device(config=device_config)

sensor_1 = 'azure_ir'
sensor_2 = 'azure_rgb'

path_ir = initialize_details(sensor_1)
path_rgb = initialize_details(sensor_2)

alpha = 0.2  # Contrast control
beta = 10  # Brightness control

if annotations_flag:
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
    ir_annotation_string = annotator.annotation_string

if annotations_flag:
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
    rgb_annotation_string = annotator.annotation_string


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
                # Write annotation data to the file
                file.write(rgb_annotation_string)

        if annotations_flag:
            anno_file1 = f'{path_i}_{frame_count:07d}.{file_extension_annotations}'
            anno_data1 = os.path.join(path_i, anno_file1)
            with open(anno_data1, 'w') as file:
                # Write annotation data to the file
                file.write(ir_annotation_string)

        frame_count += 1  # frame counter

        if cv2.waitKey(1) == ord('q'):
            break

        # Stop after 10 sec
        if time.time() - start_time >= time_to_capture:
            fps = frame_count / (time.time() - start_time)
            print(time.time() - start_time)
            print(f'FPS: {fps}')
            exit()


azure_data()
