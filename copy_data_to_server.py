import os
import csv
import shutil
import re
from datetime import datetime
from collections import OrderedDict  # To maintain column order


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
    # Convert timestamp string to datetime object
    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")


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

                # Copy associated data files to the server's data folder using regex
                regex_pattern = re.compile(
                    fr"{row['Name']}_{row['Contact_No']}_{row['Location']}_{row['Spectacles']}_{row['Age']}_{row['Run']}_(\d+)_\d+.jpeg")
                for data_file in os.listdir(data_folder_path):
                    match = regex_pattern.match(data_file)
                    if match:
                        frame_number = match.group(1)
                        new_data_file_name = f"{row['Timestamp']}_{row['Name']}_{row['Contact_No']}_{row['Location']}_{row['Gender']}_{row['Age']}_{row['Spectacles']}_{row['Run']}_{frame_number}.jpeg"
                        local_data_file_path = os.path.join(data_folder_path, data_file)
                        server_data_file_path = os.path.join(server_date_folder, new_data_file_name)
                        shutil.copy(local_data_file_path, server_data_file_path)


# Example usage
local_csv_path_system1 = r'D:\data_collector\local_metadata_system1.csv'
server_csv_path = r'D:\data_collector\server_metadata.csv'
data_folder_path_system1 = r'D:\data_collector\datafolder_system1'
server_data_folder_path = r'D:\data_collector\server_datafolder'

copy_data_to_server(local_csv_path_system1, server_csv_path, data_folder_path_system1, server_data_folder_path)
