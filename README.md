# Data-collector

## Overview

This project is dedicated to generating a large dataset for in-cabin sensing of the driver and occupants, with the ultimate goal of developing a Driver Monitoring System (DMS). The project employs a structured format for capturing and storing data, promoting efficient data management and seamless integration with in-cabin sensing systems.

## Folder Structure

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
   file_name_sensor_1 = file_constructor()
   file_name_sensor_2 = file_constructor()
    ```
   - file_name_sensor_1: The constructed file name for sensor 1.
   - file_name_sensor_2: The constructed file name for sensor 2.

## Example Usage

Refer to the example code in 'data_collector.py' for a sample implementation of data collection from two different sensors using separate threads.

## Project Goals

1. **Efficient Data Management:**
   - The structured format for capturing and storing data enhances organization and ease of access during data analysis and model development.

2. **Seamless Integration:**
   - The `initializer` module facilitates seamless integration with in-cabin sensing systems, ensuring a standardized approach to data collection across different sensors.

3. **Driver Monitoring System (DMS) Development:**
   - The generated dataset serves as a valuable resource for developing and training a Driver Monitoring System (DMS) to enhance driver and occupant safety.


## Notes

- **Data Capturing and Saving:**
  - Ensure that the actual data capturing and saving code is added to the appropriate sections of your scripts. The provided scripts include placeholders indicating where the data capturing and saving code should be incorporated.

- **User Input Validation:**
  - Validate user input to ensure it meets the expected format or criteria. This is essential for maintaining the integrity of the collected data and preventing potential errors.

- **Modular and Reusable Design:**
  - The `initializer` module encourages a modular and reusable approach, making it adaptable to different project requirements and sensors. Feel free to customize and extend the module to suit specific use cases within your project.


Author

- Created by Raafay Umar on 19-11-2023.
