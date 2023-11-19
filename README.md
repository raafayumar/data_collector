# data_collector
Data Collection Module

This Python module facilitates data collection from multiple sensors concurrently. It includes functionality for initializing task and sensor information, constructing file names, and collecting data from different sensors in separate threads.

Folder Structure

Ensure your project follows the following structure:
```bash
project_folder
│
├── initializer.py
│
└── for_2_sensor.py
│
└── data_collector.py
```
## Getting Started

1. **Import the Module:**

   Ensure that the initializer.py module is in the same directory as your Python script.

   Example:
   ```python
   from initializer import initialize_details, file_constructor
    ```
2. **Initializing Task and Sensor Information:**

   Call the initialize_details function to set up task and sensor details. This function will prompt for user input if no previous details are available.

   Example:
   ```python
   sensor_1 = input('Enter sensor 1 name: ')
   sensor_2 = input('Enter sensor 2 name: ')
   path_sensor_1 = initialize_details(sensor_1)
   path_sensor_2 = initialize_details(sensor_2)
    ```
   - path_sensor_1: Path to the directory where data for sensor 1 will be stored.
   - path_sensor_2: Path to the directory where data for sensor 2 will be stored.

4. **Constructing File Names:**

   Use the file_constructor function to construct file names based on user information and lux values.

   Example:
   ```python
   name_sensor_1 = file_constructor()
    ```
   - name_sensor_1: The constructed file name for sensor 1.

## Example Usage

Refer to the example code in 'data_collector.py' for a sample implementation of data collection from two different sensors using separate threads.

Notes

- Customize the code for specific sensors and data-capturing methods.
- Ensure the proper folder structure is maintained for data storage.

Author

- Created by Raafay Umar on 19-11-2023.
