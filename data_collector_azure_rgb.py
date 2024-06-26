"""

    This code was created by Raafay Umar on 04-11-2023.

    an example code showing the use of 'initializer' module

    to collect Data using Azure RGB Camera.

    this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”


"""

from initializer import initialize_details, file_constructor, ImageAnnotator, add_comments
import os
import time
import pykinect_azure as pykinect
import cv2
import threading
import numpy as np

# Set to 1 if rotation by 180 degree is needed.
rotate_flag = 0

# Set this to 1 for annotations, if 0 the data collection continues
annotations_flag = 0
class_names = ['WITH_SB', 'WITHOUT_SB']  # Replace with your actual class labels

# Time in sec
time_to_capture = 15

# Change file_extension, to 'npy' to save raw data
file_extension = 'npy'
file_extension_annotations = 'txt'

# Initialize the library, if the library is not found, add the library path as argument
pykinect.initialize_libraries()

# Modify camera configuration
device_config = pykinect.default_configuration
device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_1080P
device_config.depth_mode = pykinect.K4A_DEPTH_MODE_OFF
device_config.camera_fps = pykinect.K4A_FRAMES_PER_SECOND_30
# Start device
device = pykinect.start_device(config=device_config)

sensor_1 = 'azure_rgb'
path_rgb = initialize_details(sensor_1)

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
    annotation_string = annotator.annotation_string


def azure_data():
    frame_count = 0
    cv2.namedWindow('RGB Image', cv2.WINDOW_NORMAL)
    start_time = time.time()  # set timer

    while True:
        # Get the RGB image
        capture = device.update()
        ret_rgb, rgb_image = capture.get_color_image()

        if not ret_rgb:
            continue

        # get the constructed file name, with lux values for Azure RGB
        name = file_constructor()
        path = os.path.join(path_rgb, name)

        # construct the final file name
        file_name = f'{path}_{frame_count:07d}.{file_extension}'
        data = os.path.join(path, file_name)
        print(data)

        if rotate_flag:
            # Rotate the frame by 180 degree
            rgb_image = cv2.rotate(rgb_image, cv2.ROTATE_180)

        cv2.imshow('RGB Image', rgb_image)

        # check file extension and save accordingly
        if file_extension != 'npy':
            cv2.imwrite(data, rgb_image)
        else:
            np.save(data, rgb_image)

        if annotations_flag:
            anno_file = f'{path}_{frame_count:07d}.{file_extension_annotations}'
            anno_data = os.path.join(path, anno_file)
            with open(anno_data, 'w') as file:
                # Write annotation data to the file
                file.write(annotation_string)

        frame_count += 1  # frame counter

        if cv2.waitKey(1) == ord('q'):
            break

        # Stop after t sec
        if time.time() - start_time >= time_to_capture:
            fps = frame_count/(time.time() - start_time)
            print(time.time() - start_time)
            print(f'FPS: {fps}')
            comment = input('Enter Comments:')
            add_comments(comment)
            exit()


file_const = threading.Thread(target=azure_data())
file_const.start()
