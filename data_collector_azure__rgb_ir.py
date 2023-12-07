"""

    This code was created by Raafay Umar on 04-11-2023.

    an example code showing the use of 'initializer' module

    to collect Data using Azure RGB and IR.

    this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”


"""

from initializer import initialize_details, file_constructor
import os
import time
import pykinect_azure as pykinect
import cv2
import threading

# Time in sec
time_to_capture = 5

file_extension = 'jpeg'

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

        frame_count += 1

        print(data_i)
        print(data_r)

        cv2.imshow('Infrared Image', ir_image)
        cv2.imshow('RGB Image', rgb_image)
        cv2.imwrite(data_i, ir_image)
        cv2.imwrite(data_r, rgb_image)

        if cv2.waitKey(1) == ord('q'):
            break

        # Stop after 10 sec
        if time.time() - start_time >= time_to_capture:
            fps = frame_count/(time.time() - start_time)
            print(time.time() - start_time)
            print(f'FPS: {fps}')
            exit()


ir_thread = threading.Thread(target=azure_data)
ir_thread.start()
