"""

    This code was created by Raafay Umar on 04-11-2023.

    an example code showing the use of 'initializer' module

    to collect Data using RGB Camera.

    this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”


"""

from initializer import initialize_details, file_constructor, ImageAnnotator, add_comments
import os
import time
import cv2
import numpy as np

# Set to 1 if rotation by 180 degree is needed.
rotate_flag = 0

# Set this to 1 for annotations, if 0 the data collection continues
annotations_flag = 0
class_names = ['Focused', 'Distracted', 'Sleepy']  # Replace with your actual class labels

# Time in sec, if 0 then use 'S' to stop the code
time_to_capture = 0

# Change file_extension, to 'npy' to save raw data
file_extension = 'jpeg'
file_extension_annotations = 'txt'


# Initialize other RGB camera
cam = cv2.VideoCapture(0)

sensor_1 = 'intel_rgb'
path_rgb = initialize_details(sensor_1)

if annotations_flag:
    # create an object of ImageAnnotator class
    annotator = ImageAnnotator()
    annotator.set_class_names(class_names)

    # Get 1 IR frame for annotation
    r, ir = cam.read()

    if not r:
        pass

    if rotate_flag:
        # Rotate the frame by 180 degree
        ir = cv2.rotate(ir, cv2.ROTATE_180)

        # Annotate the frame using the annotator module
    annotator.annotate_frame(ir)
    annotation_string = annotator.annotation_string


def intel_data():
    frame_count = 0
    cv2.namedWindow('INTEL Image', cv2.WINDOW_NORMAL)
    start_time = time.time()  # set timer

    while True:
        ret, intel = cam.read()

        if not ret:
            pass

        # get the constructed file name, with lux values for Intel camera.
        name = file_constructor()
        path = os.path.join(path_rgb, name)

        # construct the final file name
        file_name = f'{path}_{frame_count:07d}.{file_extension}'
        data = os.path.join(path, file_name)
        print(data)

        if rotate_flag:
            # Rotate the frame by 180 degree
            intel = cv2.rotate(intel, cv2.ROTATE_180)

        cv2.imshow('INTEL Image', intel)
        cv2.imwrite(data, intel)

        if cv2.waitKey(1) == ord('q'):
            break

        # check file extension and save accordingly
        if file_extension != 'npy':
            cv2.imwrite(data, intel)
        else:
            np.save(data, intel)

        if annotations_flag:
            anno_file = f'{path}_{frame_count:07d}.{file_extension_annotations}'
            anno_data = os.path.join(path, anno_file)
            with open(anno_data, 'w') as file:

                # Write annotation data to the file
                file.write(annotation_string)
        frame_count += 1

        if time_to_capture != 0:
            if time.time() - start_time >= time_to_capture:
                fps = frame_count/(time.time() - start_time)
                print(time.time() - start_time)
                print(f'FPS: {fps}')
                comment = input('Enter Comments:')
                add_comments(comment)
                exit()

        if cv2.waitKey(1) == ord('s'):
            fps = frame_count/(time.time() - start_time)
            print(time.time() - start_time)
            print(f'FPS: {fps}')
            comment = input('Enter Comments:')
            add_comments(comment)
            exit()


intel_data()
