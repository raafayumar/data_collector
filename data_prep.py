import os
import pandas as pd
from tqdm import tqdm
import subprocess
import shutil
from datetime import datetime


def connect_to_shared_location(shared_folder, username, password):
    # Use subprocess to run net use command to connect to shared location
    command = f'net use {shared_folder} /user:{username} {password}'
    subprocess.run(command, shell=True)


def disconnect_from_shared_location(shared_folder):
    # Use subprocess to run net use command to disconnect from shared location
    command = f'net use {shared_folder} /delete'
    subprocess.run(command, shell=True)


def convert_date_format(timestamp_str):
    try:
        # Try parsing yyyy-mm-dd format
        datetime.strptime(timestamp_str, '%Y-%m-%d')
        # If successful, return the original timestamp
        return timestamp_str
    except ValueError:
        try:
            # Try parsing dd-mm-yyyy format
            date_obj = datetime.strptime(timestamp_str, '%d-%m-%Y')
            # If successful, return the timestamp formatted as yyyy-mm-dd
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            # If neither format matches, return None
            return None


def update_metadata_and_move_files(data_dir, csv_file):
    # Connect to shared location
    connect_to_shared_location(shared_folder, username, password)
    # Load CSV metadata
    df = pd.read_csv(csv_file)

    # Dictionary to keep track of runs and their corresponding first frame files
    run_first_frame = {}

    # Iterate through files in the directory tree
    for root, dirs, files in os.walk(data_dir):
        for file in tqdm(files, desc="Copying files", unit="file"):
            file_path = os.path.join(root, file)
            # Extract information from the file name
            file_name_parts = file.split('_')
            task, sensor, date = os.path.relpath(root, data_dir).split(os.path.sep)[-3:]
            name = file_name_parts[1][:2]
            contact_no = file_name_parts[2][-4:]
            location = file_name_parts[3]
            gender = file_name_parts[4]
            age = int(file_name_parts[5])
            spectacles = file_name_parts[6]
            run_number = int(file_name_parts[-2])

            # Convert the date format if it's not already in yyyy-mm-dd format
            df['Date'] = df['Date'].apply(convert_date_format)

            # Update metadata - set trail_flag to 1 for the first frame of each run
            if (
                    task, sensor, date, run_number, name, contact_no, location, gender, age,
                    spectacles) not in run_first_frame:
                run_first_frame[
                    (task, sensor, date, run_number, name, contact_no, location, gender, age, spectacles)] = True

                df.loc[(df['Task'] == task) & (df['Sensor'] == sensor) & (df['Date'] == date) & (
                        df['Name'].astype(str).str[:2] == name) & (
                               df['Contact_No'].astype(str).str.zfill(4).str[-4:] == contact_no) & (
                               df['Location'] == location) & (df['Gender'] == gender) & (df['Age'] == age) & (
                               df['Spectacles'] == spectacles) & (df['Run'] == run_number), train_test] = 1

            # Move the file to the 'Train' folder
            new_file_name = f"{task}_{sensor}_{date}_{file}"
            new_file_path = os.path.join(newfolder_path, new_file_name)
            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
            shutil.copy(file_path, new_file_path)

    # Save the updated metadata
    df.to_csv(csv_file, index=False)
    print("Metadata updated and saved successfully")
    disconnect_from_shared_location(shared_folder)


shared_folder = r'\\incabin\Incabin_DATA'
username = 'incabin'
password = 'incabin@123'
metadata_csv = r'\\incabin\incabin_data\AutoVault\metadata\metadata.csv'

data_directory = input('Absolute path of the local datafolder: ')

temp = input('\nThis data is used to? \t Press 1 or 2 \n1. Train \n2. Test\n')

if temp == '1':
    train_test = 'Train_flag'
    data_for = 'Train'
else:
    train_test = 'Test_flag'
    data_for = 'Test'

newfolder_path = os.path.join(os.path.dirname(data_directory), data_for)

print('\nlocal data path: ', data_directory)
print('local Train/Test folder path: ', newfolder_path)
print('Use this data to: ', data_for)

input("\nPress Enter to start.\n")

try:
    update_metadata_and_move_files(data_directory, metadata_csv)

except Exception as e:
    print(f"An error occurred: {e}")

input("Press Enter to exit.")
