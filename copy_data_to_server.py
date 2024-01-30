import os
import csv
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


# Modify the existing code
def copy_new_entries_to_server(local_csv_path, server_csv_path, timestamp_column='Timestamp'):
    local_data = read_local_csv(local_csv_path)
    existing_timestamps = read_existing_timestamps(server_csv_path, timestamp_column)

    unique_new_entries = [row for row in local_data if row[timestamp_column] not in existing_timestamps]

    if unique_new_entries:
        with open(server_csv_path, 'a', newline='') as server_csv:
            csv_writer = csv.DictWriter(server_csv, fieldnames=local_data[0].keys())
            if not os.path.exists(server_csv_path):
                csv_writer.writeheader()  # Write header only if the file is empty
            for row in unique_new_entries:
                csv_writer.writerow(row)


# Example usage
local_csv_path_system1 = r'D:\data_collector\local_metadata.csv'
server_csv_path = r'D:\data_collector\metadata\server_metadata.csv'

copy_new_entries_to_server(local_csv_path_system1, server_csv_path)
