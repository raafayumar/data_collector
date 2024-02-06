import os
import csv
import shutil
import re
from collections import OrderedDict  # To maintain column order
from tqdm import tqdm
import subprocess  # Add this import for subprocess

current_path = os.getcwd()

def connect_to_shared_location(shared_folder, username, password):
    # Use subprocess to run net use command to connect to shared location
    command = f'net use {shared_folder} /user:{username} {password}'
    subprocess.run(command, shell=True)


def disconnect_from_shared_location(shared_folder):
    # Use subprocess to run net use command to disconnect from shared location
    command = f'net use {shared_folder} /delete'
    subprocess.run(command, shell=True)


def read_existing_timestamps(server_csv_path, timestamp_column='Timestamp'):
    existing_timestamps = set()
    try:
        with open(server_csv_path, 'r') as server_csv:
            csv_reader = csv.DictReader(server_csv)
            for row in csv_reader:
                existing_timestamps.add(row[timestamp_column])
    except FileNotFoundError:
        pass  # File not found, it's okay, no existing data yet
    return existing_timestamps


def read_local_csv(local_csv_path):
    local_data = []
    try:
        with open(local_csv_path, 'r') as local_csv:
            csv_reader = csv.DictReader(local_csv)
            for row in csv_reader:
                local_data.append(OrderedDict(row))  # Maintain column order
    except FileNotFoundError:
        pass  # File not found, it's okay, no local data yet
    return local_data


def convert_timestamp_format(timestamp_str):
    temp = timestamp_str
    # Convert timestamp string to datetime object
    return temp


def copy_data_to_server(local_csv_path, server_csv_path, data_folder_path, server_data_folder_path,
                        timestamp_column='Timestamp'):
    try:
        # Connect to shared location
        connect_to_shared_location(shared_folder, username, password)

        timestamp_pattern = r'\d+-\d+'
        lux_values_pattern = r'\d{5}'
        traffic_pattern = r'\d{4}-\d{4}'
        frame_num_pattern = r'\d{7}'

        local_data = read_local_csv(local_csv_path)
        existing_timestamps = read_existing_timestamps(server_csv_path, timestamp_column)

        # Convert existing timestamps to datetime objects for comparison
        existing_timestamps = {convert_timestamp_format(ts) for ts in existing_timestamps}

        unique_new_entries = [row for row in local_data if
                              convert_timestamp_format(row[timestamp_column]) not in existing_timestamps]

        if unique_new_entries:
            with open(server_csv_path, 'a', newline='') as server_csv:
                csv_writer = csv.DictWriter(server_csv, fieldnames=local_data[0].keys())
                if not os.path.exists(server_csv_path):
                    csv_writer.writeheader()  # Write header only if the file is empty
                for row in unique_new_entries:
                    csv_writer.writerow(row)

                    # Construct data folder path on the server based on the structure
                    server_task_folder = os.path.join(server_data_folder_path, row['Task'])
                    server_sensor_folder = os.path.join(server_task_folder, row['Sensor'])
                    server_date_folder = os.path.join(server_sensor_folder, row['Date'])

                    # Ensure that the server directories exist
                    os.makedirs(server_date_folder, exist_ok=True)
                    name = row['Name']
                    ph_no = row['Contact_No']
                    name_pattern = name[:2]
                    contact_pattern = ph_no[-4:]
                    run_temp = str(row['Run'])
                    run_pattern = run_temp.zfill(2)

                    # Create individual variables for each field
                    location_pattern = re.escape(row["Location"])
                    gender_pattern = re.escape(row["Gender"])
                    age_pattern = re.escape(row["Age"])
                    spectacles_pattern = re.escape(row["Spectacles"])

                    # Modify the regex pattern using these variables
                    regex_pattern = re.compile(
                        f'{timestamp_pattern}_{name_pattern}_{contact_pattern}_{location_pattern}_{gender_pattern}_{age_pattern}_'
                        f'{spectacles_pattern}_{lux_values_pattern}_{traffic_pattern}_{run_pattern}_{frame_num_pattern}.+')
                    print(regex_pattern)
                    # Filter files using regex pattern
                    filtered_files = [f for f in
                                      os.listdir(os.path.join(data_folder_path, row['Task'], row['Sensor'], row['Date']))
                                      if re.search(regex_pattern, f)]
                    print(len(os.listdir(os.path.join(data_folder_path, row['Task'], row['Sensor'], row['Date']))))
                    # Copy only matching files from local to server
                    for file in tqdm(filtered_files, desc="Copying files", unit="file"):
                        # print(file)
                        local_file_path = os.path.join(data_folder_path, row['Task'], row['Sensor'], row['Date'], file)
                        server_file_path = os.path.join(server_date_folder, file)
                        shutil.copy(local_file_path, server_file_path)
    finally:
        # Disconnect from shared location regardless of success or failure
        disconnect_from_shared_location(shared_folder)


server_csv_path = r'\\incabin\incabin_data\AutoVault\metadata\metadata.csv'
server_data_folder_path = r'\\incabin\incabin_data\AutoVault\datafolder'

shared_folder = r'\\incabin\Incabin_DATA'
username = 'incabin'
password = 'incabin@123'

data_folder_path_system1 = os.path.join(current_path, 'datafolder')
local_csv_path_system1 = os.path.join(current_path, r'metadata\metadata.csv')

print('local datafolder path:', data_folder_path_system1)
print('local metadata path:', local_csv_path_system1)

input("\nPress Enter to start.\n")

try:
    copy_data_to_server(local_csv_path_system1, server_csv_path, data_folder_path_system1, server_data_folder_path)

except Exception as e:
    print(f"An error occurred: {e}")

input("Press Enter to exit.")
