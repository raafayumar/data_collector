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
delete_selected_files = 0

# Convert frames to video? set this flag to 1 if yes.
convert_frames_to_video = 0

# change file name.
video_output_path = 'test.mp4'

# Copy extracted files to a different folder of your choice, set flag to 1.
copy_extracted_files = 0

# Specify the destination folder where you want to copy the files
copy_destination_folder = r'extracted_data'

# Specify the path to the data folder
data_folder_path = r'\\incabin\incabin_data\AutoVault\datafolder'

# Set the details of the data to be extracted, leave it empty for 'all' conditions
task = ''
selected_sensor = ''
date_pattern = ''
location = ''
gender = ''
age = ''
spectacles = ''
extension = ''
name_pattern = ''
contact_num_pattern = ''
run_pattern = ''


def find_matching_files(data_folder_path, task, selected_sensor, location, gender, age, spectacles, extension):
    print('Searching...')
    files_paths = []

    for task_folder in os.listdir(data_folder_path):
        # Check if task matches the pattern
        if re.search(rf'{task}', task_folder):
            for sensor_folder in os.listdir(os.path.join(data_folder_path, task_folder)):
                # Check if selected_sensor matches the pattern
                if re.search(rf'{selected_sensor}', sensor_folder):
                    for date_folder in os.listdir(os.path.join(data_folder_path, task_folder, sensor_folder)):
                        if re.search(rf'{date_pattern}', date_folder):
                            files = [f for f in
                                     os.listdir(
                                         os.path.join(data_folder_path, task_folder, sensor_folder, date_folder))]
                            # Define the regex pattern based on the user's selected criteria
                            pattern = (
                                f'{timestamp_pattern}_{name_pattern}_{contact_num_pattern}_{location}_{gender}_{age}_'
                                f'{spectacles}_{lux_values_pattern}_{traffic_pattern}_{run_pattern}_{frame_num_pattern}.{extension}')
                            # Filter files using regex pattern
                            filtered_files = [f for f in files if re.search(pattern, f)]
                            filtered_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
                            for file in filtered_files:
                                files_paths.append(
                                    os.path.join(data_folder_path, task_folder, sensor_folder, date_folder, file))

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

result = find_matching_files(data_folder_path, task, selected_sensor, location, gender, age, spectacles, extension)
print(len(result))


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f'Deleted: {file_path}')
    except Exception as e:
        print(f'Error deleting {file_path}: {e}')


def create_video_from_frames(frames_paths, output_path):
    # Read the first frame to get its size
    initial_frame = cv2.imread(frames_paths[0])
    height, width, _ = initial_frame.shape
    # Calculating fps from the file
    first_fps = os.path.basename(frames_paths[0]).replace('-', '.').split('_')
    last_fps = os.path.basename(frames_paths[-1]).replace('-', '.').split('_')
    delta_t = float(last_fps[0]) - float(first_fps[0])
    fps = int(len(result) / delta_t) + 1
    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Write frames to the video
    for frame_path in tqdm(frames_paths, desc="Creating video", unit="frames"):
        frame = cv2.imread(frame_path)
        video_writer.write(frame)

    # Release the VideoWriter
    video_writer.release()


def copy_files_to_destination(files_paths, destination_folder):
    print('Copying files...')
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for file_path in tqdm(files_paths, desc="Copying files", unit="file"):
        copy_destination_path = os.path.join(destination_folder, file_path)
        # Copy the file to the destination folder
        shutil.copyfile(file_path, copy_destination_path)

    print('Copy completed.')


if copy_extracted_files:
    print('Total files found:', len(result))
    confirm_copy_files = input(
        f"Do you want to copy the files to {os.path.join(os.getcwd(), copy_destination_folder)} ?\n'yes' or 'y' to confirm:\n")
    if confirm_copy_files.lower() in ['yes', 'y']:
        copy_files_to_destination(result, copy_destination_folder)

if convert_frames_to_video:
    print('Total files found:', len(result))
    confirm_video_creation = input(f"{os.path.join(os.getcwd(), video_output_path)} create video?\n'y' to confirm:\n")
    if confirm_video_creation.lower() == 'y':
        frames = [file for file in result if os.path.splitext(file)[1] != '.txt']
        create_video_from_frames(frames, video_output_path)

if delete_selected_files:
    confirm_data_deletion = input("ARE YOU SURE, WANT TO DELETE DATA?\n'yes' to confirm:\n")
    if confirm_data_deletion.lower() == 'yes':
        for file_path in result:
            delete_file(file_path)
