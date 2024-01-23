"""

    This code was created by Raafay Umar on 04-11-2023.

    an example code showing the use of 'initializer' module

    to collect Data using Azure IR and annotate the data.

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
time_to_capture = 10

# Change file_extension, to 'npy' to save raw data
file_extension = 'png'
file_extension_annotations = 'txt'

# Initialize the library, if the library is not found, add the library path as argument
pykinect.initialize_libraries()

# Modify camera configuration
device_config = pykinect.default_configuration
device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_OFF
device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED
device_config.camera_fps = pykinect.K4A_FRAMES_PER_SECOND_30
# Start device
device = pykinect.start_device(config=device_config)

sensor_1 = 'azure_ir'
path_ir = initialize_details(sensor_1)

alpha = 0.2  # Contrast control
beta = 0.009  # Brightness control

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
    annotation_string = annotator.annotation_string


def azure_data():
    frame_count = 0
    cv2.namedWindow('IR Image', cv2.WINDOW_NORMAL)
    start_time = time.time()  # set timer

    while True:
        # Get the IR image
        capture = device.update()
        ret_ir, ir_image = capture.get_ir_image()
        ir_image = ir_image.astype(np.int32)

        if not ret_ir:
            pass

        # get the constructed file name, with lux values for Azure IR
        name = file_constructor()
        path = os.path.join(path_ir, name)

        # construct the final file name
        file_name = f'{path}_{frame_count:07d}.{file_extension}'
        data = os.path.join(path, file_name)
        print(data)

        if rotate_flag:
            # Rotate the frame by 180 degree
            ir_image = cv2.rotate(ir_image, cv2.ROTATE_180)

        # call convertScaleAbs function, just for visualisation
        adjusted = cv2.convertScaleAbs(ir_image, alpha=alpha, beta=beta)
        cv2.imshow('IR Image', adjusted)

        # check file extension and save accordingly
        if file_extension != 'npy':
            cv2.imwrite(data, adjusted)
        else:
            np.save(data, ir_image)

        if annotations_flag:
            anno_file = f'{path}_{frame_count:07d}.{file_extension_annotations}'
            anno_data = os.path.join(path, anno_file)
            with open(anno_data, 'w') as file:
                # Write annotation data to the file
                file.write(annotation_string)

        frame_count += 1  # frame counter

        if cv2.waitKey(1) == ord('q'):
            break

        # Stop after time_to_capture sec
        if time.time() - start_time >= time_to_capture:
            fps = frame_count/(time.time() - start_time)
            print(time.time() - start_time)
            print(f'FPS: {fps}')
            comment = input('Enter Comments:')
            add_comments(comment)
            exit()


ir_thread = threading.Thread(target=azure_data)
ir_thread.start()
