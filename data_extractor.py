"""

    This code was created by Raafay Umar on 19-11-2023.

    an example code to extract data and converts frames to videos.

    this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”


"""

import os
import re
import cv2
import shutil
from tqdm import tqdm

# Set this Flag, to delete selected files from the database.
delete_flag = 0

# Convert frames to video? set this flag to 1 if yes.
frame_to_video_flag = 1

# change file name.
output_video_path = 'test.mp4'

# Copy extracted files to a different folder of your choice, set flag to 1.
copy_files_flag = 0

# Specify the destination folder where you want to copy the files
destination_folder = r'extracted_data'

# Set the details of the data to be extracted, leave it empty for 'all' conditions
task = 'driver_face'
selected_sensor = 'azure_rgb'
date_pattern = '2024-02-13'
location = 'cc'
gender = 'm'
age = '26'
spectacles = 'ng'
extension = ''
name_pattern = 'na'
contact_num_pattern = '9806'
run_pattern = '01'

path_to_data = r'\\incabin\incabin_data\AutoVault\datafolder'


def extract_files(path_to_data, task, selected_sensor, location, gender, age, spectacles, extension):
    print('Searching...')
    files_paths = []

    for task_folder in os.listdir(path_to_data):
        # Check if task matches the pattern
        if re.search(rf'{task}', task_folder):
            for sensor_folder in os.listdir(os.path.join(path_to_data, task_folder)):
                # Check if selected_sensor matches the pattern
                if re.search(rf'{selected_sensor}', sensor_folder):
                    for date_folder in os.listdir(os.path.join(path_to_data, task_folder, sensor_folder)):
                        if re.search(rf'{date_pattern}', date_folder):
                            files = [f for f in
                                     os.listdir(os.path.join(path_to_data, task_folder, sensor_folder, date_folder))]
                            # Rest of your code to filter files based on user-specified criteria

                            # Define the regex pattern based on the user's selected criteria
                            pattern = (
                                f'{timestamp_pattern}_{name_pattern}_{contact_num_pattern}_{location}_{gender}_{age}_'
                                f'{spectacles}_{lux_values_pattern}_{traffic_pattern}_{run_pattern}_{frame_num_pattern}.{extension}')
                            # print(pattern)

                            # Filter files using regex pattern
                            filtered_files = [f for f in files if re.search(pattern, f)]
                            filtered_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
                            for file in filtered_files:
                                files_paths.append(
                                    os.path.join(path_to_data, task_folder, sensor_folder, date_folder, file))

    return files_paths


# Pattern for regex
timestamp_pattern = r'\d+-\d+'
contact_num_pattern = r'\d{4}' if not contact_num_pattern else contact_num_pattern
lux_values_pattern = r'\d{5}'
traffic_pattern = r'\d{4}-\d{4}'
frame_num_pattern = r'\d{7}'
date_pattern = r'\d{4}-\d{2}-\d{2}' if not date_pattern else date_pattern
name_pattern = '[a-zA-Z]{2}' if not name_pattern else name_pattern
run_pattern = r'\d{2}' if not run_pattern else run_pattern
location = '[a-zA-Z]{2}' if not location else location
gender = '[a-zA-Z]{1}' if not gender else gender
age = r'\d{2}' if not age else age
spectacles = '[a-zA-Z]{2}' if not spectacles else spectacles

result = extract_files(path_to_data, task, selected_sensor, location, gender, age, spectacles, extension)
# print(result)
print(len(result))


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f'Deleted: {file_path}')
    except Exception as e:
        print(f'Error deleting {file_path}: {e}')


def frames_to_video(frames_paths, output_path):
    # Read the first frame to get its size
    first_frame = cv2.imread(frames_paths[0])
    height, width, _ = first_frame.shape
    # Calculating fps from the file
    first_fps = os.path.basename(frames_paths[0]).replace('-', '.').split('_')
    last_fps = os.path.basename(frames_paths[-1]).replace('-', '.').split('_')
    delta_t = float(last_fps[0]) - float(first_fps[0])
    fps = int(len(result)/delta_t) + 1
    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Write frames to the video
    for frame_path in tqdm(frames_paths, desc="Creating video", unit="frames"):
        frame = cv2.imread(frame_path)
        video_writer.write(frame)

    # Release the VideoWriter
    video_writer.release()


def copy_to(files_paths, destination_folder):
    print('Copying files...')
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for file_path in tqdm(files_paths, desc="Copying files", unit="file"):
        file_name = os.path.basename(file_path)
        destination_path = os.path.join(destination_folder, file_name)

        # Copy the file to the destination folder
        shutil.copyfile(file_path, destination_path)

    print('Copy completed.')


if copy_files_flag:
    print('Total files found:', len(result))
    confirm_copyfiles = input(
        f"Do you want to copy the files to {os.path.join(os.getcwd(), destination_folder)} ?\n'yes' or 'y' to confirm:\n")
    if confirm_copyfiles == 'yes' or confirm_copyfiles == 'YES' or confirm_copyfiles == 'y' or confirm_copyfiles == 'Y':
        copy_to(result, destination_folder)

if frame_to_video_flag:
    print('Total files found:', len(result))
    confirm_video = input(f"{os.path.join(os.getcwd(), output_video_path)} create video?\n'y' to confirm:\n")
    if confirm_video == 'y':
        frames = []
        for files in result:
            _, ext = os.path.splitext(files)
            if ext != '.txt':
                frames.append(files)
        frames_to_video(frames, output_video_path)

if delete_flag:
    confirm_delete = input("ARE YOU SURE, WANT TO DELETE DATA?\n'yes' to confirm:\n")
    if confirm_delete == 'yes':
        for file_path in result:
            delete_file(file_path)
