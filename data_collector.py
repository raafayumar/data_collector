"""

    This code was created by Raafay Umar on 19-11-2023.

    an example code showing the use of 'initializer' module.

    this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”


"""

from initializer import initialize_details, file_constructor, add_comments
import os
import numpy as np
import time

# Time in sec
time_to_capture = 5

# Initialize task and user
sensor_name = input("Enter the sensor name: ").lower()
data_dir = initialize_details(sensor_name)
arr = []  # empty array

frame_count = 0
file_extension = 'npy'
start_time = time.time()  # set timer

while True:
    # get the constructed file name, with lux values
    file_name = file_constructor()

    # construct the final file name
    file_path = os.path.join(data_dir, f'{file_name}_{frame_count:07d}.{file_extension}')
    print(file_path)

    frame_count += 1
    np.save(file_path, arr)  # save data, replace 'arr' by actual data, 'arr' is empty array used for example
    time.sleep(0.02)  # can remove this in actual code

    # stop the code after 5 secs
    if time.time() - start_time >= time_to_capture:
        fps = frame_count / (time.time() - start_time)
        print(time.time() - start_time)
        print(f'FPS: {fps}')
        comment = input('Enter Comments:')
        add_comments(comment)
        exit()
