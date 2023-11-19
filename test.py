"""

    This code was created by Raafay Umar on 04-11-2023 from CIT.

    an example code showing the use of 'initializer' module.


"""

from initializer import initialize_details, file_constructor
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
device_config.depth_mode = pykinect.K4A_DEPTH_MODE_PASSIVE_IR

# Start device
device = pykinect.start_device(config=device_config)
sensor_1 = input('Enter sensor 1 name: ')
sensor_2 = input('Enter sensor 2 name: ')

path_sensor_1 = initialize_details(sensor_1)
path_sensor_2 = initialize_details(sensor_2)


def ir_data():
    frame_count = 0
    cv2.namedWindow('Infrared Image', cv2.WINDOW_NORMAL)
    t = time.time()  # set timer

    while True:
        # get the constructed file name, with lux values
        name = file_constructor()
        path = os.path.join(path_sensor_1, name)
        # construct the final file name
        file_name = f'{path}_{frame_count:07d}.{file_extension}'
        data = os.path.join(path, file_name)

        frame_count += 1

        capture = device.update()

        # Get the infrared image
        ret, ir_image = capture.get_ir_image()
        print(data)

        if not ret:
            pass

        cv2.imshow('Infrared Image', ir_image)
        cv2.imwrite(data, ir_image)

        if time.time() - t >= 5:
            print(time.time() - t)
            exit()


ir_thread = threading.Thread(target=ir_data)
ir_thread.start()


def rgb_data():
    frame_count = 0
    cv2.namedWindow('RGB Image', cv2.WINDOW_NORMAL)
    while True:
        # get the constructed file name, with lux values
        name = file_constructor()
        path = os.path.join(path_sensor_2, name)
        # construct the final file name
        file_name = f'{path}_{frame_count:07d}.{file_extension}'
        data = os.path.join(path, file_name)

        frame_count += 1

        capture = device.update()

        # Get the infrared image
        ret, color_image = capture.get_color_image()
        print(data)

        if not ret:
            pass

        cv2.imshow('RGB Image', color_image)
        cv2.imwrite(data, color_image)


rgb_thread = threading.Thread(target=rgb_data)
rgb_thread.start()
