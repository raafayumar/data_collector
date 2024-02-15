# Data-collector

## Important Note

Before initiating any data collection, make sure to always update your local repository with the latest changes by running:

```bash
git pull origin main
```

## Overview

This project is dedicated to generating a large dataset for in-cabin sensing of the driver and occupants, with the ultimate goal of developing a Driver Monitoring System (DMS). The project employs a structured format for capturing and storing data, promoting efficient data management and seamless integration with in-cabin sensing systems.

# Getting Started

## Installation Requirements

Clone this repo
   - Open a folder/location of choice and shift+right click on the background of the Explorer window, then click on "Open command window here" or "Open PowerShell window here". then run this command:
     
```bash
   git clone https://github.com/raafayumar/data_collector.git
```

Before using this module, make sure to install the required dependencies by running the following command on the same cmd window:

```bash
   pip install -r requirements.txt
```
Additionally, please install the `Azure Kinect Sensor SDK` by following the instructions provided in the [Azure Kinect Sensor SDK](https://github.com/microsoft/Azure-Kinect-Sensor-SDK/blob/develop/docs/usage.md)

## Ready-to-Use Scripts

These scripts are pre-configured, ensuring a seamless start to your data collection without the need for additional modifications. Below, you'll find the scripts corresponding to Azure IR, RGB, and Intel cameras.

### Scripts:

1. **Azure IR Camera:**
   - **Script Name:** `data_collector_azure_ir.py`

2. **Azure RGB Camera:**
   - **Script Name:** `data_collector_azure_rgb.py`
     
3. **Azure RGB & IR Camera:**
   -  **Script Name:** `data_collector_azure_rgb_ir.py`

4. **Intel Camera:**
   - **Script Name:** `data_collector_Intel.py`


# How-to and Script Usage
1. **Import the Module:**

   Ensure that the initializer.py and annotator.py module are in the same directory as your Python script.

   Example:
   ```python
   from initializer import initialize_details, file_constructor, ImageAnnotator, add_comments
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

3. **Create an Annotator Object:**
   Create an object of the ImageAnnotator class in your script.
   Example:
   ```python
   annotator = ImageAnnotator()
   ```

4. **Set Class Names:**
   Define the class names relevant to your annotation task using the set_class_names method.
   Example:
   ```python
   class_names = ['Class1', 'Class2', 'Class3']
   annotator.set_class_names(class_names)
   ```

5. **Annotate Frames:**
   Use the annotate_frame method to annotate each frame captured during the data collection process.
   Example:
   ```python
   annotator.annotate_frame(rgb_image)
   annotation_string = annotator.annotation_string
   ```
    - rgb_image: The RGB frame to be annotated.
    - The annotation information is stored in the annotation_string attribute.

6. **Constructing File Names:**

    -  Use the file_constructor function to construct file names based on user information and lux values.
    -  Refer to this [Google Doc](https://docs.google.com/document/d/1W_o_zSktdUY45XnXvFC2Fec4VeORDSuNmJsk8lIC-UI/edit?usp=sharing) for the naming scheme.
   
   Example:
   ```python
   file_name_sensor_1 = file_constructor()
   file_name_sensor_2 = file_constructor()
    ```
   - file_name_sensor_1: The constructed file name for sensor 1.
   - file_name_sensor_2: The constructed file name for sensor 2.

8. **User Comments and Metadata:**

   A new function `add_comments` has been added to collect user comments at the end of each run and create a metadata CSV file. The metadata includes the following information: Task, Sensor, Date, Timestamp, Name, Contact_No, Location, Gender, Age, Spectacles, Run,   Comments, Trail_flag, Test_flag.

## Data Collection with Annotations

In the example code `data_collector.py`, you'll find a variable named `annotations_flag`. This variable controls whether the script performs data annotations or continues data collection. Here's how it works:

- Set `annotations_flag = 1` if you want to annotate the data whilst collecting. When this flag is set to 1, the script will use the `ImageAnnotator` module to interactively annotate frames from the sensor(s). Annotations include selecting bounding boxes and assigning class labels.

- Set `annotations_flag = 0` if you want to continue data collection without annotations. In this mode, the script will solely focus on capturing data frames from the sensor(s) without any interactive annotation.

Make sure to adjust the value of `annotations_flag` and edit the `class_names` based on your specific use case.

## Data Extraction and Manipulation

The `data_extractor.py` code provides options for processing data and exporting results.

**Usage**
  - Set the details of the data to be extracted, leave it empty for 'all' conditions.
    
  - Set frame_to_video_flag to 1 if you want to convert frames to a video.
     - Specify the output_video_path for the generated video.
       
  - Set delete_flag to 1 if you want to delete selected files from the database.
    
  - Set copy_files_flag to 1 if you want to copy extracted files to a different folder.
     - Specify the destination_folder where you want to copy the files.

**Note:**
Make sure to check the path of the `datafolder` to ensure accurate data extraction.   
## Example Usage

Refer to the example code in 'data_collector_for_2_sensor.py' for a sample implementation of data collection from two different sensors using separate threads.

## Data Transfer to Server

To streamline the process of transferring data to the server, a convenient `data_transfer.exe` tool is provided. Follow the steps below to transfer your data seamlessly:

**Usage:**
1. Run the `data_transfer.exe` executable by double-clicking on it.
2. When prompted, provide the absolute path for the `datafolder` and `metadata` directories on your local system.
3. The tool will automatically transfer the data to the server, following the predefined folder structure.

**Important Note:**
Ensure that you are connected to the network named 'TP-Link_866C' or have a reliable Ethernet cable plugged in for successful data transfer.

This tool simplifies the data transfer process, making it efficient and user-friendly.

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


## Acknowledgments

This project utilizes the PyKinect SDK for interfacing with Azure sensors and capturing data seamlessly. The `pyKinectAzure` SDK was created by [Ibai Gorordo](https://github.com/ibaiGorordo).


Author

- Created by Raafay Umar on 19-11-2023.
