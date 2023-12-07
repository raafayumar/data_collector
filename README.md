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
├── annotator.py
│
└── for_2_sensor.py
│
└── data_collector.py
```
# Getting Started

## Installation Requirements

Before using this  module, make sure to install the required dependencies by running the following command:

```bash
   pip install -r requirements.txt
```
Additionally, please install the `Azure Kinect Sensor SDK` by following the instructions provided in the [Azure Kinect Sensor SDK](https://github.com/microsoft/Azure-Kinect-Sensor-SDK/blob/develop/docs/usage.md)

## Data Collection with Annotations

In the example code `data_collector.py`, you'll find a variable named `annotations_flag`. This variable controls whether the script performs data annotations or continues data collection. Here's how it works:

- Set `annotations_flag = 1` if you want to annotate the collected data. When this flag is set to 1, the script will use the `ImageAnnotator` module to interactively annotate frames from the sensor(s). Annotations include selecting bounding boxes and assigning class labels.

- Set `annotations_flag = 0` if you want to continue data collection without annotations. In this mode, the script will solely focus on capturing data frames from the sensor(s) without any interactive annotation.

Make sure to adjust the value of `annotations_flag` based on your specific use case.

## Extracting Data and Converting Frames to Videos

The `data_extractor.py` code demonstrates how to extract data and convert frames to videos using the generated dataset.

**Usage**
   - Set frame_to_video_flag to 1 if you want to convert frames to a video.
   - Specify the output_video_path for the generated video.
# Data collection
1. **Import the Module:**

   Ensure that the initializer.py and annotator.py module are in the same directory as your Python script.

   Example:
   ```python
   from initializer import initialize_details, file_constructor
   from annotator import ImageAnnotator

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

7. **Constructing File Names:**

   Use the file_constructor function to construct file names based on user information and lux values.

   Example:
   ```python
   file_name_sensor_1 = file_constructor()
   file_name_sensor_2 = file_constructor()
    ```
   - file_name_sensor_1: The constructed file name for sensor 1.
   - file_name_sensor_2: The constructed file name for sensor 2.

## Example Usage

Refer to the example code in 'data_collector_for_2_sensor.py' for a sample implementation of data collection from two different sensors using separate threads.

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
