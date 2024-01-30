import os
import csv
import shutil
import re
from collections import OrderedDict  # To maintain column order
from tqdm import tqdm

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
                # Copy associated data files to the server's data folder using regex
                regex_pattern = re.compile(
                    f'{timestamp_pattern}_{name_pattern}_{contact_pattern}_{row["Location"]}_{row["Gender"]}_{row["Age"]}_'
                    f'{row["Spectacles"]}_{lux_values_pattern}_{traffic_pattern}_{run_pattern}_{frame_num_pattern}.{extension}')

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


timestamp_pattern = r'\d+-\d+'
lux_values_pattern = r'\d{5}'
traffic_pattern = r'\d{4}-\d{4}'
frame_num_pattern = r'\d{7}'
run_pattern = r'\d{2}'
extension = ''
# Example usage
local_csv_path_system1 = r'\\cit\DATA_on_server\Raafay\metadata\metadata.csv'
server_csv_path = r'\\incabin\incabin_data\metadata\metadata.csv'

data_folder_path_system1 = r'\\cit\DATA_on_server\Raafay\datafolder'
server_data_folder_path = r'\\incabin\incabin_data\datafolder'

copy_data_to_server(local_csv_path_system1, server_csv_path, data_folder_path_system1, server_data_folder_path)
