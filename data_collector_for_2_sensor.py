"""

    This code was created by Raafay Umar on 19-11-2023.

    an example code showing the use of 'initializer' module.

    this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”


"""

from initializer import initialize_details, file_constructor
import os
import threading

file_extension = 'jpeg'

sensor_1 = input('Enter sensor 1 name: ')
sensor_2 = input('Enter sensor 2 name: ')

path_sensor_1 = initialize_details(sensor_1)
path_sensor_2 = initialize_details(sensor_2)


def capture_data_sensor_1():
    frame_count = 0

    while True:
        # get the constructed file name, with lux values
        name = file_constructor()
        path = os.path.join(path_sensor_1, name)
        # construct the final file name
        file_name = f'{path}_{frame_count:07d}.{file_extension}'
        data = os.path.join(path, file_name)

        frame_count += 1

        # Add data capturing and saving code for sensor 1 here


thread_1 = threading.Thread(target=capture_data_sensor_1)
thread_1.start()


def capture_data_sensor_2():
    frame_count = 0

    while True:
        # get the constructed file name, with lux values
        name = file_constructor()
        path = os.path.join(path_sensor_2, name)
        # construct the final file name
        file_name = f'{path}_{frame_count:07d}.{file_extension}'
        data = os.path.join(path, file_name)

        frame_count += 1
        # Add data capturing and saving code for sensor 2 here


thread_2 = threading.Thread(target=capture_data_sensor_2)
thread_2.start()
