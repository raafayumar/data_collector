"""

    This code was created by Raafay Umar on 19-11-2023.

    an example code showing the use of 'initializer' module.


"""

from initializer import initialize_details, file_constructor
import os
import numpy as np
import time

# Initialize task and user
sensor_name = input("Enter the sensor name: ").lower()
data_dir = initialize_details(sensor_name)
arr = []

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
    np.save(file_path, arr)  # save data, replace 'arr' by actual data
    time.sleep(0.02)  # can remove this in actual code

    # stop the code after 5 secs
    if time.time() - start_time >= 5:
        fps = frame_count / (time.time() - start_time)
        print(time.time() - start_time)
        print(f'FPS: {fps}')
        exit()

