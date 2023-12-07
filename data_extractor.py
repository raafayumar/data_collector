"""

    This code was created by Raafay Umar on 19-11-2023.

    an example code to extract data and converts frames to videos.

    this is the filename:
    “timestamp_name_phone-number_location_gender_age_spectacles_lux_traffic_run-number_frame-number.extension”


"""


import os
import re
import cv2

# Convert frames to video? set this flag to 1 if yes.
frame_to_video_flag = 0
output_video_path = 'output_video.mp4'  # change file name.

# Example usage:
path_to_data = r'datafolder'

task = 'driver_face'
selected_sensor = 'azure_ir'
location = 'la'
gender = 'm'
age = '24'
spectacles = 'ng'
extension = 'jpeg'


def extract_files(path_to_data, task, selected_sensor, location, gender, age, spectacles, extension):
    files_paths = []

    for task_folder in os.listdir(path_to_data):
        # Check if task matches the pattern
        if re.search(rf'{task}', task_folder):
            for sensor_folder in os.listdir(os.path.join(path_to_data, task_folder)):
                # Check if selected_sensor matches the pattern
                if re.search(rf'{selected_sensor}', sensor_folder):
                    for date_folder in os.listdir(os.path.join(path_to_data, task_folder, sensor_folder)):
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

                        for file in filtered_files:
                            files_paths.append(
                                os.path.join(path_to_data, task_folder, sensor_folder, date_folder, file))

    return files_paths


# Pattern for regex
timestamp_pattern = r'\d+-\d+'
name_pattern = r'[a-zA-Z]{2}'
contact_num_pattern = r'\d{4}'
lux_values_pattern = r'\d{5}'
run_pattern = r'\d{2}'
traffic_pattern = r'\d{4}-\d{4}'
frame_num_pattern = r'\d{7}'

result = extract_files(path_to_data, task, selected_sensor, location, gender, age, spectacles, extension)
print(len(result))


def frames_to_video(frames_paths, output_path, fps=30):
    # Read the first frame to get its size
    first_frame = cv2.imread(frames_paths[0])
    height, width, _ = first_frame.shape

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Write frames to the video
    for frame_path in frames_paths:
        print(frame_path)
        frame = cv2.imread(frame_path)
        video_writer.write(frame)

    # Release the VideoWriter
    video_writer.release()


if frame_to_video_flag:
    frames_to_video(result, output_video_path)
