"""

    This code was created by Raafay Umar on 04-11-2023.

    an example code showing the use of 'initializer' module

    to collect Data using Azure RGB, IR and any other RGB Camera.


"""

from initializer import initialize_details, file_constructor
from test_annotator import ImageAnnotator
import os
import time
import pykinect_azure as pykinect
import cv2
import threading

file_extension = 'jpeg'

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

# Replace with your actual class labels
class_names = ['CLASS1', 'CLASS2', 'CLASS3']

# create an object of ImageAnnotator class
annotator = ImageAnnotator()
annotator.set_class_names(class_names)

# Get the RGB image
capture = device.update()
ret_rgb, rgb_image = capture.get_color_image()

if not ret_rgb:
    print('ret no')
    pass

# Annotate the frame using the annotator module
annotator.annotate_frame(rgb_image)
annotation_string = annotator.annotation_string


def azure_data():
    frame_count = 0
    cv2.namedWindow('RGB Image', cv2.WINDOW_NORMAL)
    start_time = time.time()  # set timer

    while True:

        capture = device.update()

        # Get the RGB image
        ret_rgb, rgb_image = capture.get_color_image()

        if not ret_rgb:
            print('ret no')
            pass

        # get the constructed file name, with lux values for Azure RGB
        name = file_constructor()
        path = os.path.join(path_rgb, name)

        # construct the final file name
        file_name = f'{path}_{frame_count:07d}.{file_extension}'
        anno_file = f'{path}_{frame_count:07d}.txt'
        data = os.path.join(path, file_name)
        anno_data = os.path.join(path, anno_file)
        frame_count += 1
        print(data)

        cv2.imshow('RGB Image', rgb_image)
        cv2.imwrite(data, rgb_image)

        with open(anno_data, 'w') as file:
            # Write a string to the file
            file.write(annotation_string)

        if cv2.waitKey(1) == ord('q'):
            break

        # Stop after t sec
        if time.time() - start_time >= 5:
            fps = frame_count/(time.time() - start_time)
            print(time.time() - start_time)
            print(f'FPS: {fps}')
            exit()


rgb_thread = threading.Thread(target=azure_data)
rgb_thread.start()
