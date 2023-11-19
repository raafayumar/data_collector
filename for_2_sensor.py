"""

    This code was created by Raafay Umar on 04-11-2023 from CIT.

    an example code showing the use of 'initializer' module.


"""

from initializer import initialize_details, file_constructor
import os
import time
import threading

file_extension = 'jpeg'

sensor_1 = input('Enter sensor 1 name: ')
sensor_2 = input('Enter sensor 2 name: ')

path_sensor_1 = initialize_details(sensor_1)
path_sensor_2 = initialize_details(sensor_2)


def ir_data():
    frame_count = 0
    t = time.time()  # set timer

    while True:
        # get the constructed file name, with lux values
        name = file_constructor()
        path = os.path.join(path_sensor_1, name)
        # construct the final file name
        file_name = f'{path}_{frame_count:07d}.{file_extension}'
        data = os.path.join(path, file_name)

        frame_count += 1

        # Add data capturing and saving code for sensor 1 here

        if time.time() - t >= 5:
            print(time.time() - t)
            exit()


ir_thread = threading.Thread(target=ir_data)
ir_thread.start()


def rgb_data():
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


rgb_thread = threading.Thread(target=rgb_data)
rgb_thread.start()
